from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.pg_models import User
from app.models.schemas import CheckoutResponse, SubscribeRequest
from app.services.billing_service import create_checkout_session, handle_stripe_webhook

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/subscribe", response_model=CheckoutResponse)
async def subscribe(
    req: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        url = await create_checkout_session(db, current_user.id, req.price_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return CheckoutResponse(checkout_url=url)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        await handle_stripe_webhook(db, payload, sig_header)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"received": True}
