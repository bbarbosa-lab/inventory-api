from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequestIn(BaseModel):
    email: EmailStr


class PasswordResetConfirmIn(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12, max_length=128)


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    detail: str
