"""Authentication routes: signup, login, and current-user."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    WalletNonceRequest,
    WalletNonceResponse,
    WalletVerifyRequest,
)
from app.schemas.user import UserCreate, UserRead
from app.services import wallet as wallet_svc
from app.services.auth import (
    EmailAlreadyRegisteredError,
    authenticate_email_user,
    signup_email_user,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        user = await signup_email_user(db, payload.email, payload.password, payload.display_name)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exc
    await db.commit()
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_email_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return _token_response(user)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


# --------------------------------- wallet ----------------------------------


@router.post("/wallet/nonce", response_model=WalletNonceResponse)
async def wallet_nonce(payload: WalletNonceRequest) -> WalletNonceResponse:
    message, token = wallet_svc.issue_nonce(payload.address)
    return WalletNonceResponse(message=message, nonce_token=token)


@router.post("/wallet/verify", response_model=TokenResponse)
async def wallet_verify(
    payload: WalletVerifyRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    try:
        address = wallet_svc.verify_signature(
            payload.address, payload.signature, payload.nonce_token
        )
    except wallet_svc.WalletVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    user = await wallet_svc.login_or_create_wallet_user(db, address)
    await db.commit()
    return _token_response(user)


@router.post("/wallet/link", response_model=UserRead)
async def wallet_link(
    payload: WalletVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    try:
        address = wallet_svc.verify_signature(
            payload.address, payload.signature, payload.nonce_token
        )
        await wallet_svc.link_wallet_to_user(db, user, address)
    except wallet_svc.WalletVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except wallet_svc.WalletAlreadyLinkedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet already linked to another account",
        ) from exc
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)
