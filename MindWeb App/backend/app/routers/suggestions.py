import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.middleware.auth_middleware import get_current_user
from app.middleware.rate_limiter import (
    get_cached_suggestions,
    get_suggestion_count_today,
    increment_suggestion_count,
)
from app.models.pg_models import TierEnum, User
from app.models.schemas import SuggestionSet
from app.services.suggestion_service import get_suggestions_for_user
from app.db.neo4j import get_neo4j_session
from app.services.graph_service import count_user_nodes

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.get("", response_model=SuggestionSet)
async def fetch_suggestions(
    current_user: User = Depends(get_current_user),
    neo4j_session=Depends(get_neo4j_session),
):
    # Enforce free-tier daily suggestion limit
    if current_user.tier == TierEnum.free:
        count_today = get_suggestion_count_today(current_user.id)
        if count_today >= settings.FREE_SUGGESTIONS_PER_DAY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Free tier limit of {settings.FREE_SUGGESTIONS_PER_DAY} suggestions/day reached. Upgrade to premium.",
            )

    node_count = await count_user_nodes(neo4j_session, current_user.id)

    # Try cache first
    cached_json = get_cached_suggestions(current_user.id)
    cached_set: SuggestionSet | None = None
    if cached_json:
        try:
            cached_set = SuggestionSet.model_validate_json(cached_json)
        except Exception:
            cached_set = None

    result = await get_suggestions_for_user(current_user.id, node_count, cached_set)

    # Track usage for free tier
    if current_user.tier == TierEnum.free:
        increment_suggestion_count(current_user.id)

    return result
