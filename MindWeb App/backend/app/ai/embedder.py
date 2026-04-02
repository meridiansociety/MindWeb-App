"""
Generates 1536-dimensional vector embeddings for extracted entities
using OpenAI text-embedding-3-small.
"""
import uuid

from openai import OpenAI

from app.config import settings
from app.models.schemas import EmbeddedEntity, Entity

_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def embed_entities(entities: list[Entity]) -> list[EmbeddedEntity]:
    if not entities:
        return []

    texts = [e.label for e in entities]

    response = _client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        timeout=20,
    )

    embedded: list[EmbeddedEntity] = []
    for entity, emb_data in zip(entities, response.data):
        embedded.append(
            EmbeddedEntity(
                entity=entity,
                embedding=emb_data.embedding,
                node_id=uuid.uuid4(),
            )
        )

    return embedded
