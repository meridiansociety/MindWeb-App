import uuid
from datetime import datetime, timezone

from neo4j import AsyncSession

from app.models.schemas import EdgeResponse, GraphPayload, NodeDetailResponse, NodeResponse


async def create_node(
    session: AsyncSession,
    user_id: uuid.UUID,
    node_id: uuid.UUID,
    label: str,
    node_type: str,
    entry_id: uuid.UUID,
) -> None:
    await session.run(
        """
        MERGE (n:Node {id: $id, user_id: $user_id})
        ON CREATE SET
            n.label       = $label,
            n.type        = $type,
            n.entry_id    = $entry_id,
            n.created_at  = $created_at
        """,
        id=str(node_id),
        user_id=str(user_id),
        label=label,
        type=node_type,
        entry_id=str(entry_id),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


async def create_edge(
    session: AsyncSession,
    user_id: uuid.UUID,
    source_id: uuid.UUID,
    target_id: uuid.UUID,
    edge_type: str,
    weight: float,
    inferred: bool = True,
) -> None:
    await session.run(
        """
        MATCH (a:Node {id: $source_id, user_id: $user_id})
        MATCH (b:Node {id: $target_id, user_id: $user_id})
        MERGE (a)-[r:CONNECTED {type: $edge_type}]->(b)
        ON CREATE SET r.weight = $weight, r.inferred = $inferred
        ON MATCH  SET r.weight = $weight
        """,
        user_id=str(user_id),
        source_id=str(source_id),
        target_id=str(target_id),
        edge_type=edge_type,
        weight=weight,
        inferred=inferred,
    )


async def get_graph(
    session: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 500,
    offset: int = 0,
) -> GraphPayload:
    node_result = await session.run(
        """
        MATCH (n:Node {user_id: $user_id})
        WITH n
        ORDER BY n.created_at DESC
        SKIP $offset LIMIT $limit
        OPTIONAL MATCH (n)-[r:CONNECTED]-(m:Node {user_id: $user_id})
        RETURN n, count(r) AS connection_count
        """,
        user_id=str(user_id),
        limit=limit,
        offset=offset,
    )
    nodes: list[NodeResponse] = []
    node_ids: set[str] = set()
    async for record in node_result:
        n = record["n"]
        node_ids.add(n["id"])
        nodes.append(
            NodeResponse(
                id=uuid.UUID(n["id"]),
                label=n["label"],
                type=n["type"],
                created_at=datetime.fromisoformat(n["created_at"]),
                connection_count=record["connection_count"],
            )
        )

    edge_result = await session.run(
        """
        MATCH (a:Node {user_id: $user_id})-[r:CONNECTED]->(b:Node {user_id: $user_id})
        WHERE a.id IN $node_ids AND b.id IN $node_ids
        RETURN a.id AS source, b.id AS target, r.type AS type,
               r.weight AS weight, r.inferred AS inferred
        """,
        user_id=str(user_id),
        node_ids=list(node_ids),
    )
    edges: list[EdgeResponse] = []
    async for record in edge_result:
        edges.append(
            EdgeResponse(
                source_id=uuid.UUID(record["source"]),
                target_id=uuid.UUID(record["target"]),
                type=record["type"],
                weight=record["weight"],
                inferred=record["inferred"],
            )
        )

    return GraphPayload(nodes=nodes, edges=edges)


async def get_node_detail(
    session: AsyncSession,
    user_id: uuid.UUID,
    node_id: uuid.UUID,
) -> NodeDetailResponse | None:
    result = await session.run(
        """
        MATCH (n:Node {id: $node_id, user_id: $user_id})
        OPTIONAL MATCH (n)-[r:CONNECTED]-(m:Node {user_id: $user_id})
        RETURN n,
               count(r) AS connection_count,
               collect({
                   source_id: startNode(r).id,
                   target_id: endNode(r).id,
                   type:      r.type,
                   weight:    r.weight,
                   inferred:  r.inferred
               }) AS edges
        """,
        node_id=str(node_id),
        user_id=str(user_id),
    )
    record = await result.single()
    if record is None:
        return None

    n = record["n"]
    raw_edges = [e for e in record["edges"] if e["source_id"] is not None]
    return NodeDetailResponse(
        id=uuid.UUID(n["id"]),
        label=n["label"],
        type=n["type"],
        created_at=datetime.fromisoformat(n["created_at"]),
        connection_count=record["connection_count"],
        edges=[
            EdgeResponse(
                source_id=uuid.UUID(e["source_id"]),
                target_id=uuid.UUID(e["target_id"]),
                type=e["type"],
                weight=e["weight"],
                inferred=e["inferred"],
            )
            for e in raw_edges
        ],
    )


async def delete_node(
    session: AsyncSession,
    user_id: uuid.UUID,
    node_id: uuid.UUID,
) -> bool:
    result = await session.run(
        """
        MATCH (n:Node {id: $node_id, user_id: $user_id})
        DETACH DELETE n
        RETURN count(n) AS deleted
        """,
        node_id=str(node_id),
        user_id=str(user_id),
    )
    record = await result.single()
    return record is not None and record["deleted"] > 0


async def count_user_nodes(session: AsyncSession, user_id: uuid.UUID) -> int:
    result = await session.run(
        "MATCH (n:Node {user_id: $user_id}) RETURN count(n) AS total",
        user_id=str(user_id),
    )
    record = await result.single()
    return record["total"] if record else 0
