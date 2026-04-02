import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TierEnum(str, PyEnum):
    free = "free"
    premium = "premium"


class EntryStatusEnum(str, PyEnum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class SubscriptionStatusEnum(str, PyEnum):
    active = "active"
    cancelled = "cancelled"
    past_due = "past_due"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[TierEnum] = mapped_column(
        Enum(TierEnum), default=TierEnum.free, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    entries: Mapped[list["KnowledgeEntry"]] = relationship(
        "KnowledgeEntry", back_populates="user", cascade="all, delete-orphan"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="user", uselist=False
    )


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[EntryStatusEnum] = mapped_column(
        Enum(EntryStatusEnum), default=EntryStatusEnum.pending, nullable=False
    )
    nodes_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="entries")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SubscriptionStatusEnum] = mapped_column(
        Enum(SubscriptionStatusEnum), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="subscription")
