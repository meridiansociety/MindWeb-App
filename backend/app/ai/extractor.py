"""
Entity extraction from freeform user text using GPT-4o with structured output.
Returns up to MAX_ENTITIES_PER_ENTRY entities per input.
"""
import json

from openai import OpenAI

from app.config import settings
from app.models.schemas import Entity

_client = OpenAI(api_key=settings.OPENAI_API_KEY)

_SYSTEM_PROMPT = """You are a knowledge entity extractor.
Given a piece of freeform text describing what a user has learned or is thinking about,
extract distinct knowledge entities. Each entity must be one of:
  - concept     (an idea, theory, principle, or mental model)
  - book        (a book title)
  - author      (a person's name, academic or practitioner)
  - skill       (a practical or technical skill)

Return ONLY a valid JSON array — no prose, no markdown, no explanation.
Each element: { "label": string, "type": "concept"|"book"|"author"|"skill", "confidence_score": float 0-1 }

Rules:
- Maximum {max_entities} entities.
- Omit duplicates.
- Omit vague filler phrases (e.g. "interesting stuff", "things").
- confidence_score reflects how clearly the text identifies this as a distinct entity.
- If no clear entities exist, return [].
""".replace("{max_entities}", str(settings.MAX_ENTITIES_PER_ENTRY))


def extract_entities(raw_text: str) -> list[Entity]:
    response = _client.chat.completions.create(
        model=settings.EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.2,
        max_tokens=800,
        timeout=25,
    )

    content = response.choices[0].message.content or "[]"

    try:
        raw = json.loads(content)
    except json.JSONDecodeError:
        return []

    entities: list[Entity] = []
    seen_labels: set[str] = set()
    valid_types = {"concept", "book", "author", "skill"}

    for item in raw:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "")).strip()
        etype = str(item.get("type", "")).strip().lower()
        score = float(item.get("confidence_score", 0.0))

        if not label or etype not in valid_types:
            continue
        if label.lower() in seen_labels:
            continue

        seen_labels.add(label.lower())
        entities.append(Entity(label=label, type=etype, confidence_score=score))

        if len(entities) >= settings.MAX_ENTITIES_PER_ENTRY:
            break

    return entities
