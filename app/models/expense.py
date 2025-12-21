"""
Expense SQLModel

Represents expense records extracted from receipts.
"""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Numeric

from app.models.category import ExpenseCategory


if TYPE_CHECKING:
    from app.models.user import User


class ExpenseBase(SQLModel):
    """Base expense fields shared across schemas."""
    merchant: str = Field(max_length=255, description="Name of the merchant/store")
    amount: Decimal = Field(
        sa_column=Column(Numeric(10, 2)),
        description="Total amount in decimal format"
    )
    date: datetime = Field(description="Date of the expense/transaction")
    category: ExpenseCategory = Field(
        default=ExpenseCategory.OTHER,
        description="Category of the expense"
    )
    is_subscription: bool = Field(
        default=False,
        description="Whether this is a recurring subscription"
    )


class Expense(ExpenseBase, table=True):
    """
    Expense database model.
    
    Attributes:
        id: Primary key, auto-generated
        user_id: Foreign key to the user who owns this expense
        merchant: Name of the merchant/store
        amount: Transaction amount (up to 10 digits, 2 decimal places)
        date: Date of the transaction
        category: Category enum (Food, Transport, etc.)
        is_subscription: Whether it's a recurring expense
        receipt_url: URL to the stored receipt image in Supabase
        created_at: Timestamp when record was created
        user: Relationship back to the user
    """
    __tablename__ = "expenses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    receipt_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to stored receipt image in Supabase Storage"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="expenses")


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense manually."""
    pass


class ExpenseRead(ExpenseBase):
    """Schema for expense API responses."""
    id: int
    user_id: int
    receipt_url: Optional[str] = None
    created_at: datetime


class ExpenseFromReceipt(SQLModel):
    """Schema for OCR-extracted expense data."""
    merchant: str
    amount: Decimal
    date: datetime
    category: ExpenseCategory
