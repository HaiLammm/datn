from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


# Role type for type safety
UserRole = Literal["job_seeker", "recruiter", "admin"]


class Msg(BaseModel):
    msg: str


class UserVerify(BaseModel):
    email: EmailStr
    activation_code: str


class PasswordChangeWithOTP(BaseModel):
    otp: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"



class TokenPayload(BaseModel):
    sub: Optional[EmailStr] = None  # User email (primary identifier)
    user_id: Optional[str] = None   # User ID as string
    email: Optional[EmailStr] = None  # User email (duplicate for clarity)
    role: Optional[UserRole] = None   # User role
    type: str = "access"              # Token type (access/refresh)
    exp: Optional[int] = None         # Expiration timestamp