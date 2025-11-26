from pydantic import BaseModel, Field, EmailStr, field_validator
import utils
REGEX_USERNAME = r"^[a-z]{6,}$"
special_chars = "!@#$%^&*"


class UserCreate(BaseModel):
    user_name: str = Field(..., pattern=REGEX_USERNAME)
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator('password')
    @classmethod
    def validate_password_complete(cls, password: str) -> str:
        if not any(map(lambda x: x.isupper(), password)):
            raise ValueError('Mat khau phai co Chu hoa')
        elif not any(map(lambda x: x in special_chars, password)):
            raise ValueError('Mat khau phai co ky tu dac biet')
        else:
            return password
