import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    user_id: uuid.UUID
    access_token: str
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Entries ───────────────────────────────────────────────────────────────────

class KnowledgeInputRequest(BaseModel):
    text: str = Field(min_length=3, max_length=1000)


class EntryResponse(BaseModel):
    entry_id: uuid.UUID
    status: str
    nodes_created: int = 0


# ── Graph ─────────────────────────────────────────────────────────────────────

class EdgeResponse(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    type: str
    weight: float
    inferred: bool


class NodeResponse(BaseModel):
    id: uuid.UUID
    label: str
    type: str
    created_at: datetime
    connection_count: int


class NodeDetailResponse(NodeResponse):
    edges: list[EdgeResponse] = []


class GraphPayload(BaseModel):
    nodes: list[NodeResponse]
    edges: list[EdgeResponse]


# ── Suggestions ───────────────────────────────────────────────────────────────

class SuggestionItem(BaseModel):
    label: str
    rationale: str
    confidence: float


class SuggestionSet(BaseModel):
    adjacent: list[SuggestionItem]
    bridge: list[SuggestionItem]
    gap: list[SuggestionItem]


# ── Billing ───────────────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    price_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str


# ── Internal AI types (not exposed via API) ───────────────────────────────────

class Entity(BaseModel):
    label: str
    type: str  # concept | book | author | skill
    confidence_score: float


class EmbeddedEntity(BaseModel):
    entity: Entity
    embedding: list[float]
    node_id: uuid.UUID | None = None


class Edge(BaseModel):
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    edge_type: str
    weight: float
