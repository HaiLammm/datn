from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.modules.auth.dependencies import get_current_active_user
from app.modules.auth.schemas import (
    Msg,
    PasswordChangeWithOTP,
    Token,
    UserVerify,
    UserLogin,
    ForgotPasswordRequest,
    ResetPassword,
)
from app.modules.auth.services import AuthService
from app.modules.users.models import User
from app.modules.users.schemas import User as UserSchema
from app.modules.users.schemas import UserCreate
from app.modules.users.services import UserService

router = APIRouter()


@router.post("/register", response_model=Msg, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Register a new user, create an activation code and send it via email.
    """
    db_user = user_service.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed_password = get_password_hash(user_in.password)
    activation_code = auth_service.generate_activation_code()
    activation_code_expires_at = datetime.utcnow() + timedelta(minutes=5)

    user = user_service.create_user(
        db=db,
        user_in=user_in,
        hashed_password=hashed_password,
        activation_code=activation_code,
        activation_code_expires_at=activation_code_expires_at,
    )

    # TODO: Send activation email using background tasks
    # print(f"Activation code for {user.email}: {activation_code}")

    return {"msg": "User registered successfully. Please check your email for activation."}


@router.post("/verify-email", response_model=UserSchema)
def verify_email(
    activation_data: UserVerify,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Verify a user's email account.
    """
    user = auth_service.activate_user(
        db, email=activation_data.email, activation_code=activation_data.activation_code
    )
    return user



@router.post("/login", response_model=Token)
def login_for_access_token(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = auth_service.authenticate_user(
        db, email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request-password-change", response_model=Msg)
def request_password_change(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Request a password change by sending an OTP to the user's email (for logged-in users).
    """
    otp = auth_service.request_password_change(db, user=current_user)
    # TODO: Send password reset email using background tasks
    # print(f"Password reset OTP for {current_user.email}: {otp}")
    return {"msg": "Password change OTP sent to your email."}


@router.post("/change-password", response_model=Msg)
def change_password(
    password_data: PasswordChangeWithOTP,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Change user password using an OTP (for logged-in users).
    """
    auth_service.change_password(
        db,
        user=current_user,
        otp=password_data.otp,
        new_password=password_data.new_password,
    )
    return {"msg": "Password changed successfully"}


@router.post("/forgot-password", response_model=Msg)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Forgot Password
    """
    otp = auth_service.request_password_reset(db, email=request.email)
    # TODO: Send password reset email using background tasks
    # print(f"Password reset OTP for {request.email}: {otp}")
    return {"msg": "Password reset OTP sent to your email."}


@router.post("/reset-password", response_model=Msg)
def reset_password(
    password_data: ResetPassword,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Reset password with OTP.
    """
    auth_service.reset_password_with_code(
        db,
        email=password_data.email,
        otp=password_data.otp,
        new_password=password_data.new_password,
    )
    return {"msg": "Password has been reset successfully."}

