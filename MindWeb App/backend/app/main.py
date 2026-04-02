from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.neo4j import close_driver
from app.db.postgres import engine
from app.models.pg_models import Base
from app.routers import auth, billing, entries, graph, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create PostgreSQL tables on startup (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_driver()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://app.mindweb.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(entries.router, prefix=API_PREFIX)
app.include_router(graph.router, prefix=API_PREFIX)
app.include_router(suggestions.router, prefix=API_PREFIX)
app.include_router(billing.router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
