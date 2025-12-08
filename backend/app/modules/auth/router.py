from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    create_refresh_token,
)
from app.core.config import settings
from app.core.mailer import send_email
from app.modules.auth.dependencies import (
    get_current_active_user,
    get_current_user_from_refresh_token,
)
from app.modules.auth.schemas import (
    AccessToken,
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
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
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

    background_tasks.add_task(
        send_email,
        recipients=[user.email],
        subject="Account Activation",
        template_name="activation.html",
        template_body={
            "full_name": user.full_name or user.email,
            "activation_code": activation_code,
            "project_name": settings.PROJECT_NAME,
        },
    )

    return {
        "msg": "User registered successfully. Please check your email for activation."
    }


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
        db,
        email=activation_data.email,
        activation_code=activation_data.activation_code,
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token", response_model=AccessToken)
def refresh_token(
    current_user: User = Depends(get_current_user_from_refresh_token),
) -> Any:
    """
    OAuth2 compatible token refresh, get a new access token
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    new_access_token = create_access_token(data={"sub": current_user.email})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/request-password-change", response_model=Msg)
async def request_password_change(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Request a password change by sending an OTP to the user's email (for logged-in users).
    """
    otp = auth_service.request_password_change(db, user=current_user)
    background_tasks.add_task(
        send_email,
        recipients=[current_user.email],
        subject="Password Reset Request",
        template_name="reset_password.html",
        template_body={
            "full_name": current_user.full_name or current_user.email,
            "otp": otp,
            "project_name": settings.PROJECT_NAME,
        },
    )
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
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(AuthService),
) -> Any:
    """
    Forgot Password
    """
    otp = auth_service.request_password_reset(db, email=request.email)
    if otp:
        background_tasks.add_task(
            send_email,
            recipients=[request.email],
            subject="Password Reset Request",
            template_name="reset_password.html",
            template_body={
                "full_name": request.email,
                "otp": otp,
                "project_name": settings.PROJECT_NAME,
            },
        )
    return {
        "msg": "If an account with that email exists, a password reset OTP will be sent."
    }


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
