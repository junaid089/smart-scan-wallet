"""
Token Schemas

Pydantic models for authentication tokens.
"""
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """OAuth2 token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    type: Optional[str] = None
