---
name: MindWeb Project
description: MindWeb — personal knowledge graph SaaS app, tech stack, architecture, and build status
type: project
---

MindWeb is a personal knowledge graph SaaS app being built from scratch.

**Why:** User wants a product where people submit freeform text ("what did you learn?"), an AI pipeline extracts entities, and a graph of interconnected knowledge nodes is built and visualized.

**Stack:**
- Frontend: React 18 + Vite, React Flow (graph), TailwindCSS, Zustand
- Backend: Python FastAPI, Celery (async tasks), Pydantic v2
- Databases: PostgreSQL (users/entries/subscriptions), Neo4j (graph nodes/edges), Pinecone (vector store)
- AI: OpenAI GPT-4o (entity extraction), text-embedding-3-small (embeddings), LangChain
- Infra: Redis (Celery broker + cache), Stripe (billing), Docker Compose + Nginx
- Auth: JWT (24h access token, 30d refresh token), passlib/bcrypt

**Architecture:** Three-tier — React SPA → FastAPI → data layer. AI pipeline runs as async Celery worker triggered per knowledge entry submission.

**Tiers:**
- Free: 50 nodes max, 3 suggestions/day
- Premium: unlimited

**Build status:** Scaffolding and full initial construction started 2026-04-02.

**How to apply:** All code should follow the blueprint exactly. Neo4j queries always scoped by user_id. Pinecone namespaced by user_id. Max 10 entities per entry, similarity threshold 0.78, Celery timeout 30s.
