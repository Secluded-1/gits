"""
Pydantic-модели для валидации данных.
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MaterialCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=50, max_length=10000)


class MaterialOut(BaseModel):
    id: int
    title: str
    text_length: int
    created_at: str