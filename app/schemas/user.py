"""
User Schemas

Pydantic models for user-related API requests and responses.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)"
    )


class UserLogin(BaseModel):
    """Schema for user login request (alternative to OAuth2 form)."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user API responses."""
    id: int
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """Schema for user with hashed password (internal use)."""
    hashed_password: str
