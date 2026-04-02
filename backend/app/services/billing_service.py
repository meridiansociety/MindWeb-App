import uuid

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.pg_models import Subscription, SubscriptionStatusEnum, TierEnum, User

stripe.api_key = settings.STRIPE_SECRET_KEY


async def get_user_tier(db: AsyncSession, user_id: uuid.UUID) -> TierEnum:
    result = await db.execute(select(User.tier).where(User.id == user_id))
    tier = result.scalar_one_or_none()
    return tier or TierEnum.free


async def check_node_limit(
    db: AsyncSession, user_id: uuid.UUID, current_node_count: int
) -> tuple[bool, str]:
    tier = await get_user_tier(db, user_id)
    if tier == TierEnum.premium:
        return True, ""
    if current_node_count >= settings.FREE_MAX_NODES:
        return False, f"Free tier limit of {settings.FREE_MAX_NODES} nodes reached. Upgrade to premium."
    return True, ""


async def create_checkout_session(
    db: AsyncSession, user_id: uuid.UUID, price_id: str
) -> str:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError("User not found")

    customer_id = user.stripe_customer_id
    if customer_id is None:
        customer = stripe.Customer.create(email=user.email)
        customer_id = customer.id
        user.stripe_customer_id = customer_id
        await db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://app.mindweb.io/settings?checkout=success",
        cancel_url="https://app.mindweb.io/settings?checkout=cancelled",
        metadata={"user_id": str(user_id)},
    )
    return session.url


async def handle_stripe_webhook(db: AsyncSession, payload: bytes, sig_header: str) -> None:
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise ValueError("Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id_str = session.get("metadata", {}).get("user_id")
        if not user_id_str:
            return
        user_id = uuid.UUID(user_id_str)
        await _upgrade_user(db, user_id, session["subscription"])

    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        await _sync_subscription(db, sub)


async def _upgrade_user(
    db: AsyncSession, user_id: uuid.UUID, stripe_subscription_id: str
) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return

    user.tier = TierEnum.premium

    stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    sub = sub_result.scalar_one_or_none()
    if sub is None:
        sub = Subscription(user_id=user_id)
        db.add(sub)

    sub.stripe_subscription_id = stripe_subscription_id
    sub.status = SubscriptionStatusEnum.active
    from datetime import datetime, timezone
    sub.current_period_end = datetime.fromtimestamp(
        stripe_sub["current_period_end"], tz=timezone.utc
    )
    await db.commit()


async def _sync_subscription(db: AsyncSession, stripe_sub: dict) -> None:
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    sub = result.scalar_one_or_none()
    if sub is None:
        return

    status_map = {
        "active": SubscriptionStatusEnum.active,
        "canceled": SubscriptionStatusEnum.cancelled,
        "past_due": SubscriptionStatusEnum.past_due,
    }
    sub.status = status_map.get(stripe_sub["status"], SubscriptionStatusEnum.past_due)

    if sub.status == SubscriptionStatusEnum.cancelled:
        user_result = await db.execute(select(User).where(User.id == sub.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.tier = TierEnum.free

    await db.commit()
