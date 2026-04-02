import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.neo4j import get_neo4j_session
from app.db.postgres import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.pg_models import KnowledgeEntry, User
from app.models.schemas import EntryResponse, KnowledgeInputRequest
from app.services.billing_service import check_node_limit
from app.services.graph_service import count_user_nodes

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("", response_model=EntryResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_entry(
    req: KnowledgeInputRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    neo4j_session=Depends(get_neo4j_session),
):
    # Check node limit before enqueuing
    node_count = await count_user_nodes(neo4j_session, current_user.id)
    allowed, reason = await check_node_limit(db, current_user.id, node_count)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

    entry = KnowledgeEntry(user_id=current_user.id, raw_text=req.text)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    # Enqueue Celery task
    from app.tasks.pipeline import run_pipeline
    run_pipeline.delay(str(entry.id), req.text, str(current_user.id))

    return EntryResponse(entry_id=entry.id, status=entry.status.value)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KnowledgeEntry).where(
            KnowledgeEntry.id == entry_id,
            KnowledgeEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    return EntryResponse(
        entry_id=entry.id,
        status=entry.status.value,
        nodes_created=entry.nodes_created,
    )
