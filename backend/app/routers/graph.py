import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.neo4j import get_neo4j_session
from app.middleware.auth_middleware import get_current_user
from app.models.pg_models import User
from app.models.schemas import GraphPayload, NodeDetailResponse
from app.services.graph_service import (
    delete_node,
    get_graph,
    get_node_detail,
)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphPayload)
async def fetch_graph(
    limit: int = Query(default=500, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    neo4j_session=Depends(get_neo4j_session),
):
    return await get_graph(neo4j_session, current_user.id, limit=limit, offset=offset)


@router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
async def fetch_node(
    node_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    neo4j_session=Depends(get_neo4j_session),
):
    node = await get_node_detail(neo4j_session, current_user.id, node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node


@router.delete("/nodes/{node_id}", status_code=status.HTTP_200_OK)
async def remove_node(
    node_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    neo4j_session=Depends(get_neo4j_session),
):
    deleted = await delete_node(neo4j_session, current_user.id, node_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return {"deleted": True}
