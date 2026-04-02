from pinecone import Pinecone, Index

from app.config import settings

_client: Pinecone | None = None


def get_pinecone() -> Pinecone:
    global _client
    if _client is None:
        _client = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _client


def get_index() -> Index:
    return get_pinecone().Index(settings.PINECONE_INDEX_NAME)
