"""
Celery task: full AI pipeline per knowledge entry.

Sequence:
  1. Mark entry as processing
  2. Extract entities  (GPT-4o)
  3. Generate embeddings  (text-embedding-3-small)
  4. Infer + persist edges  (Pinecone → Neo4j)
  5. Generate suggestions  (GPT-4o + Neo4j topology)
  6. Cache suggestions  (Redis, TTL 1h)
  7. Mark entry as complete

Celery task timeout: 30 s hard kill: 35 s (set in celery_worker.py).
Retries: 3x with exponential backoff on any exception.
"""
import json
import uuid

from celery import Task
from celery.utils.log import get_task_logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.ai.edge_inferrer import infer_and_persist_edges
from app.ai.embedder import embed_entities
from app.ai.extractor import extract_entities
from app.ai.suggestion_engine import generate_suggestions
from app.config import settings
from app.db.neo4j import get_sync_driver
from app.db.pinecone import get_index
from app.middleware.rate_limiter import cache_suggestions
from app.models.pg_models import EntryStatusEnum, KnowledgeEntry

logger = get_task_logger(__name__)

# Sync SQLAlchemy engine for Celery (asyncpg doesn't work in sync context)
_sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
_sync_engine = create_engine(_sync_db_url, pool_pre_ping=True)


def _get_sync_db() -> Session:
    return Session(_sync_engine)


def _set_entry_status(
    db: Session, entry_id: uuid.UUID, status: EntryStatusEnum, nodes_created: int = 0
) -> None:
    entry = db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == entry_id)
    ).scalar_one_or_none()
    if entry:
        entry.status = status
        if nodes_created:
            entry.nodes_created = nodes_created
        db.commit()


# Celery app import — deferred to avoid circular imports
from celery_worker import celery_app  # noqa: E402


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    soft_time_limit=settings.CELERY_TASK_TIMEOUT,
    time_limit=settings.CELERY_TASK_TIMEOUT + 5,
    name="pipeline.run",
)
def run_pipeline(
    self: Task,
    entry_id_str: str,
    raw_text: str,
    user_id_str: str,
) -> dict:
    entry_id = uuid.UUID(entry_id_str)
    user_id = uuid.UUID(user_id_str)

    db = _get_sync_db()
    neo4j_driver = get_sync_driver()
    pinecone_index = get_index()

    try:
        # ── Step 1: mark processing ───────────────────────────────────────────
        _set_entry_status(db, entry_id, EntryStatusEnum.processing)
        logger.info("Pipeline started entry=%s user=%s", entry_id, user_id)

        # ── Step 2: extract entities ──────────────────────────────────────────
        entities = extract_entities(raw_text)
        logger.info("Extracted %d entities", len(entities))

        if not entities:
            _set_entry_status(db, entry_id, EntryStatusEnum.complete, nodes_created=0)
            return {"nodes_created": 0}

        # ── Step 3: generate embeddings ───────────────────────────────────────
        embedded = embed_entities(entities)

        # ── Step 4: infer edges + persist nodes/vectors ───────────────────────
        with neo4j_driver.session() as neo4j_session:
            edges = infer_and_persist_edges(
                embedded_entities=embedded,
                user_id=user_id,
                entry_id=entry_id,
                neo4j_session=neo4j_session,
                pinecone_index=pinecone_index,
            )

            # ── Step 5: generate suggestions ──────────────────────────────────
            triggering_ids = [ee.node_id for ee in embedded if ee.node_id]
            suggestion_set = generate_suggestions(
                user_id=user_id,
                triggering_node_ids=triggering_ids,
                neo4j_session=neo4j_session,
                pinecone_index=pinecone_index,
            )

        # ── Step 6: cache suggestions (Redis, TTL 1h) ─────────────────────────
        cache_suggestions(user_id, suggestion_set.model_dump_json())

        # ── Step 7: mark complete ─────────────────────────────────────────────
        nodes_created = len(embedded)
        _set_entry_status(db, entry_id, EntryStatusEnum.complete, nodes_created=nodes_created)
        logger.info("Pipeline complete entry=%s nodes=%d edges=%d", entry_id, nodes_created, len(edges))

        return {"nodes_created": nodes_created, "edges_created": len(edges)}

    except Exception as exc:
        logger.exception("Pipeline failed entry=%s attempt=%d", entry_id, self.request.retries)
        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            _set_entry_status(db, entry_id, EntryStatusEnum.failed)
            return {"error": str(exc)}
    finally:
        db.close()
