"""
User SQLModel

Represents application users with authentication credentials.
"""
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.expense import Expense


class UserBase(SQLModel):
    """Base user fields shared across schemas."""
    email: str = Field(unique=True, index=True, max_length=255)


class User(UserBase, table=True):
    """
    User database model.
    
    Attributes:
        id: Primary key, auto-generated
        email: Unique email address, used for login
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        expenses: Relationship to user's expenses
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    
    # Relationships
    expenses: List["Expense"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(min_length=8, max_length=100)


class UserRead(UserBase):
    """Schema for user API responses."""
    id: int
    is_active: bool
