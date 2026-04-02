"""
Queries Pinecone for existing user nodes with cosine similarity above threshold.
Creates edges in Neo4j for matches. Upserts new vectors to Pinecone.

All Pinecone vectors are namespaced by user_id to enforce data isolation.
All Neo4j queries are scoped by user_id — no exceptions.
"""
import uuid

from neo4j import Session as SyncSession
from pinecone import Index

from app.config import settings
from app.models.schemas import Edge, EmbeddedEntity


def infer_and_persist_edges(
    embedded_entities: list[EmbeddedEntity],
    user_id: uuid.UUID,
    entry_id: uuid.UUID,
    neo4j_session: SyncSession,
    pinecone_index: Index,
) -> list[Edge]:
    """
    For each new embedded entity:
    1. Query Pinecone for existing nodes belonging to this user.
    2. For matches above similarity_threshold, create edges in Neo4j.
    3. Upsert the new node's vector to Pinecone.

    Returns the list of edges created.
    """
    namespace = str(user_id)
    edges: list[Edge] = []

    for ee in embedded_entities:
        node_id = ee.node_id
        assert node_id is not None

        # ── 1. Write node to Neo4j ────────────────────────────────────────────
        neo4j_session.run(
            """
            MERGE (n:Node {id: $id, user_id: $user_id})
            ON CREATE SET
                n.label      = $label,
                n.type       = $type,
                n.entry_id   = $entry_id,
                n.created_at = $created_at
            """,
            id=str(node_id),
            user_id=str(user_id),
            label=ee.entity.label,
            type=ee.entity.type,
            entry_id=str(entry_id),
            created_at=_now_iso(),
        )

        # ── 2. Query Pinecone for similar existing nodes ───────────────────────
        query_result = pinecone_index.query(
            vector=ee.embedding,
            top_k=10,
            namespace=namespace,
            include_metadata=True,
        )

        for match in query_result.matches:
            score: float = match.score
            if score < settings.SIMILARITY_THRESHOLD:
                continue

            matched_node_id_str: str = match.metadata.get("node_id", "")
            if not matched_node_id_str:
                continue

            try:
                matched_node_id = uuid.UUID(matched_node_id_str)
            except ValueError:
                continue

            if matched_node_id == node_id:
                continue

            edge_type = _infer_edge_type(
                ee.entity.type,
                match.metadata.get("type", "concept"),
                score,
            )

            neo4j_session.run(
                """
                MATCH (a:Node {id: $source_id, user_id: $user_id})
                MATCH (b:Node {id: $target_id, user_id: $user_id})
                MERGE (a)-[r:CONNECTED {type: $edge_type}]->(b)
                ON CREATE SET r.weight = $weight, r.inferred = true
                ON MATCH  SET r.weight = $weight
                """,
                user_id=str(user_id),
                source_id=str(node_id),
                target_id=str(matched_node_id),
                edge_type=edge_type,
                weight=round(score, 4),
            )

            edges.append(
                Edge(
                    source_node_id=node_id,
                    target_node_id=matched_node_id,
                    edge_type=edge_type,
                    weight=round(score, 4),
                )
            )

        # ── 3. Upsert vector to Pinecone ──────────────────────────────────────
        pinecone_index.upsert(
            vectors=[
                {
                    "id": f"{user_id}:{node_id}",
                    "values": ee.embedding,
                    "metadata": {
                        "user_id": str(user_id),
                        "node_id": str(node_id),
                        "label": ee.entity.label,
                        "type": ee.entity.type,
                    },
                }
            ],
            namespace=namespace,
        )

    return edges


def _infer_edge_type(source_type: str, target_type: str, score: float) -> str:
    if score >= 0.92:
        return "related_to"
    if source_type == "author" or target_type == "author":
        return "influenced_by"
    if source_type == "book" or target_type == "book":
        return "part_of"
    return "related_to"


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
