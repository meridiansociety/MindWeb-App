"""
Cognitive Suggestion Engine — generates three suggestion types per session:

  Adjacent — nodes semantically close to the user's recent nodes but not yet in their graph.
  Bridge   — nodes that could connect two otherwise disconnected clusters.
  Gap      — concepts that are notably absent given the user's existing knowledge topology.

All Pinecone queries are namespaced by user_id.
All Neo4j queries are scoped by user_id.
"""
import uuid

import openai
from neo4j import Session as SyncSession
from pinecone import Index

from app.config import settings
from app.models.schemas import SuggestionItem, SuggestionSet

_openai = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

_SUGGESTION_PROMPT = """You are a knowledge graph advisor.

A user's knowledge graph contains the following nodes:
{node_labels}

Based on these nodes, generate exactly 3 adjacent suggestions, 1 bridge suggestion, and 1 gap suggestion.

Definitions:
- Adjacent: concepts closely related to what the user already knows but not yet in their graph.
- Bridge: a concept that could meaningfully connect two or more of the user's existing clusters.
- Gap: a foundational concept that is conspicuously absent given what the user knows.

Return ONLY valid JSON in this exact shape — no prose, no markdown:
{{
  "adjacent": [
    {{"label": string, "rationale": string, "confidence": float}},
    {{"label": string, "rationale": string, "confidence": float}},
    {{"label": string, "rationale": string, "confidence": float}}
  ],
  "bridge": [
    {{"label": string, "rationale": string, "confidence": float}}
  ],
  "gap": [
    {{"label": string, "rationale": string, "confidence": float}}
  ]
}}
"""


def generate_suggestions(
    user_id: uuid.UUID,
    triggering_node_ids: list[uuid.UUID],
    neo4j_session: SyncSession,
    pinecone_index: Index,
) -> SuggestionSet:
    node_labels = _fetch_recent_node_labels(user_id, neo4j_session, limit=30)

    if len(node_labels) < 5:
        return _seed_suggestions()

    prompt = _SUGGESTION_PROMPT.replace("{node_labels}", ", ".join(node_labels))

    response = _openai.chat.completions.create(
        model=settings.EXTRACTION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=600,
        timeout=20,
    )

    content = response.choices[0].message.content or "{}"

    import json
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return _seed_suggestions()

    def parse_items(raw: list) -> list[SuggestionItem]:
        items = []
        for item in raw or []:
            if not isinstance(item, dict):
                continue
            items.append(
                SuggestionItem(
                    label=str(item.get("label", "")),
                    rationale=str(item.get("rationale", "")),
                    confidence=float(item.get("confidence", 0.7)),
                )
            )
        return items

    return SuggestionSet(
        adjacent=parse_items(data.get("adjacent", [])),
        bridge=parse_items(data.get("bridge", [])),
        gap=parse_items(data.get("gap", [])),
    )


def _fetch_recent_node_labels(
    user_id: uuid.UUID, session: SyncSession, limit: int = 30
) -> list[str]:
    result = session.run(
        """
        MATCH (n:Node {user_id: $user_id})
        RETURN n.label AS label
        ORDER BY n.created_at DESC
        LIMIT $limit
        """,
        user_id=str(user_id),
        limit=limit,
    )
    return [record["label"] for record in result]


def _seed_suggestions() -> SuggestionSet:
    return SuggestionSet(
        adjacent=[
            SuggestionItem(
                label="Mental Models",
                rationale="A core framework for structured thinking and decision-making.",
                confidence=0.9,
            ),
            SuggestionItem(
                label="Systems Thinking",
                rationale="Understanding how interconnected parts produce emergent behavior.",
                confidence=0.88,
            ),
            SuggestionItem(
                label="First Principles Reasoning",
                rationale="Break assumptions down to their roots for clearer insight.",
                confidence=0.85,
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
