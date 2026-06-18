from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    PasswordRecoveryRequest,
    PasswordRecoveryResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> RegisterResponse:
    try:
        user = auth_service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RegisterResponse(user=user)


@router.post("/password-recovery", response_model=PasswordRecoveryResponse)
def password_recovery(payload: PasswordRecoveryRequest) -> PasswordRecoveryResponse:
    auth_service.request_password_recovery(payload.email)
    return PasswordRecoveryResponse(
        message="If the email exists, a password recovery token has been generated."
    )


@router.post("/password-reset", response_model=PasswordResetResponse)
def password_reset(payload: PasswordResetRequest) -> PasswordResetResponse:
    try:
        auth_service.reset_password(payload.token, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PasswordResetResponse(message="Password updated successfully.")
