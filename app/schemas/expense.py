"""
Expense Schemas

Pydantic models for expense-related API requests and responses.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.category import ExpenseCategory


class ExpenseCreate(BaseModel):
    """Schema for manually creating an expense."""
    merchant: str = Field(..., max_length=255, description="Name of the merchant/store")
    amount: Decimal = Field(..., ge=0, description="Transaction amount")
    date: datetime = Field(..., description="Date of the transaction")
    category: ExpenseCategory = Field(default=ExpenseCategory.OTHER, description="Expense category")
    is_subscription: bool = Field(default=False, description="Whether this is a recurring subscription")


class ExpenseResponse(BaseModel):
    """Schema for expense API responses."""
    id: int
    user_id: int
    merchant: str
    amount: Decimal
    date: datetime
    category: ExpenseCategory
    is_subscription: bool
    receipt_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReceiptUploadResponse(BaseModel):
    """Schema for receipt upload response."""
    message: str = "Receipt processed successfully"
    expense: ExpenseResponse
    ocr_data: dict = Field(description="Raw data extracted by OCR")


class ExpenseListResponse(BaseModel):
    """Schema for listing multiple expenses."""
    items: list[ExpenseResponse]
    total: int
    page: int = 1
    page_size: int = 20
