import uuid

from app.models.schemas import SuggestionItem, SuggestionSet

# Seed suggestions shown to users with < 5 nodes (cold-start fallback)
SEED_SUGGESTIONS = SuggestionSet(
    adjacent=[
        SuggestionItem(
            label="Mental Models",
            rationale="A foundational concept for structuring how you think and learn.",
            confidence=0.9,
        ),
        SuggestionItem(
            label="Systems Thinking",
            rationale="Understanding how parts of a system interact and influence each other.",
            confidence=0.88,
        ),
    ],
    bridge=[
        SuggestionItem(
            label="Second-Order Effects",
            rationale="Bridges cause-and-effect thinking with long-term consequence analysis.",
            confidence=0.82,
        ),
    ],
    gap=[
        SuggestionItem(
            label="Deliberate Practice",
            rationale="Most learners skip structured practice — this closes a critical gap.",
            confidence=0.85,
        ),
    ],
)


async def get_suggestions_for_user(
    user_id: uuid.UUID,
    node_count: int,
    cached_suggestions: SuggestionSet | None,
) -> SuggestionSet:
    if node_count < 5:
        return SEED_SUGGESTIONS

    if cached_suggestions is not None:
        return cached_suggestions

    # Fallback when cache is empty and node count is sufficient —
    # the suggestion engine runs inside the Celery pipeline and populates
    # the cache; this path is hit only if the pipeline hasn't run yet.
    return SEED_SUGGESTIONS
