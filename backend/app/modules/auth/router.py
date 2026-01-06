from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response

from app.core.security import (
    create_access_token,
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
from app.modules.users.schemas import UserCreate, User as UserSchema


router = APIRouter()


@router.post("/register", response_model=Msg, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(AuthService),
) -> Msg:
    """
    Register a new user, create an activation code and send it via email.
    """
    user, activation_code = await auth_service.register_user(user_in=user_in)

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
async def verify_email(
    activation_data: UserVerify,
    auth_service: AuthService = Depends(AuthService),
) -> UserSchema:
    """
    Verify a user's email account.
    """
    user = await auth_service.activate_user(
        email=activation_data.email,
        activation_code=activation_data.activation_code,
    )
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    user_credentials: UserLogin,
    auth_service: AuthService = Depends(AuthService),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_service.authenticate_user(
        email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "user_id": user.id})

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token", response_model=AccessToken)
async def refresh_token(
    response: Response,
    current_user: User = Depends(get_current_user_from_refresh_token),
) -> AccessToken:
    """
    OAuth2 compatible token refresh, get a new access token
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    new_access_token = create_access_token(data={"sub": current_user.email, "role": current_user.role, "user_id": current_user.id})
    
    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/request-password-change", response_model=Msg)
async def request_password_change(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(AuthService),
) -> Msg:
    """
    Request a password change by sending an OTP to the user's email (for logged-in users).
    """
    otp = auth_service.request_password_change(user=current_user)
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
async def change_password(
    password_data: PasswordChangeWithOTP,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(AuthService),
) -> Msg:
    """
    Change user password using an OTP (for logged-in users).
    """
    await auth_service.change_password(
        user=current_user,
        otp=password_data.otp,
        new_password=password_data.new_password,
    )
    return {"msg": "Password changed successfully"}


@router.post("/forgot-password", response_model=Msg)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(AuthService),
) -> Msg:
    """
    Forgot Password
    """
    otp = await auth_service.request_password_reset(email=request.email)
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
async def reset_password(
    password_data: ResetPassword,
    auth_service: AuthService = Depends(AuthService),
) -> Msg:
    """
    Reset password with OTP.
    """
    await auth_service.reset_password_with_code(
        email=password_data.email,
        otp=password_data.otp,
        new_password=password_data.new_password,
    )
    return {"msg": "Password has been reset successfully."}


@router.post("/logout", response_model=Msg)
async def logout(response: Response) -> Msg:
    """
    Logout user by clearing authentication cookies.
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"msg": "Successfully logged out"}