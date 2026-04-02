from collections.abc import AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.config import settings

_driver: AsyncDriver | None = None


async def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def get_neo4j_session() -> AsyncGenerator[AsyncSession, None]:
    driver = await get_driver()
    async with driver.session() as session:
        yield session


# ── Sync driver for Celery tasks ──────────────────────────────────────────────

from neo4j import GraphDatabase, Driver  # noqa: E402

_sync_driver: Driver | None = None


def get_sync_driver() -> Driver:
    global _sync_driver
    if _sync_driver is None:
        _sync_driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _sync_driver
