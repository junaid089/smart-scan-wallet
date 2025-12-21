"""
Analytics Endpoints

Provides spending analytics and visualizations for expenses.
"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract
from sqlmodel import select

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.expense import Expense
from app.models.category import ExpenseCategory
from pydantic import BaseModel


router = APIRouter(prefix="/analytics", tags=["Analytics"])


# Color mapping for expense categories (optimized for charts)
CATEGORY_COLORS = {
    ExpenseCategory.FOOD: "#FF6384",          # Red-pink
    ExpenseCategory.TRANSPORT: "#36A2EB",     # Blue
    ExpenseCategory.UTILITIES: "#FFCE56",     # Yellow
    ExpenseCategory.ENTERTAINMENT: "#9966FF", # Purple
    ExpenseCategory.HEALTH: "#4BC0C0",        # Teal
    ExpenseCategory.SHOPPING: "#FF9F40",      # Orange
    ExpenseCategory.OTHER: "#C9CBCF",         # Gray
}


class CategorySpending(BaseModel):
    """Schema for category spending data point."""
    name: str
    value: float
    color: str
    count: int = 0  # Number of transactions


class MonthlyAnalyticsResponse(BaseModel):
    """Schema for monthly analytics response."""
    year: int
    month: int
    total_spending: float
    categories: list[CategorySpending]
    transaction_count: int


class SpendingTrend(BaseModel):
    """Schema for spending trend data."""
    date: str
    amount: float


@router.get(
    "/monthly",
    response_model=MonthlyAnalyticsResponse,
    summary="Get monthly spending analytics",
    description="Get spending breakdown by category for a specific month."
)
async def get_monthly_analytics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    year: Optional[int] = Query(default=None, description="Year (defaults to current)"),
    month: Optional[int] = Query(default=None, ge=1, le=12, description="Month (1-12, defaults to current)")
) -> MonthlyAnalyticsResponse:
    """
    Get monthly spending analytics grouped by category.
    
    Returns data optimized for frontend chart libraries (Chart.js, Recharts, etc.)
    with category names, amounts, and colors.
    """
    # Default to current year/month if not provided
    now = datetime.utcnow()
    target_year = year if year is not None else now.year
    target_month = month if month is not None else now.month
    
    # Query: Group expenses by category for the given month
    statement = (
        select(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count")
        )
        .where(Expense.user_id == current_user.id)
        .where(extract("year", Expense.date) == target_year)
        .where(extract("month", Expense.date) == target_month)
        .group_by(Expense.category)
    )
    
    result = await db.execute(statement)
    rows = result.all()
    
    # Build response data
    categories = []
    total_spending = Decimal("0.00")
    transaction_count = 0
    
    for row in rows:
        category = row.category
        amount = row.total or Decimal("0.00")
        count = row.count or 0
        
        total_spending += amount
        transaction_count += count
        
        categories.append(CategorySpending(
            name=category.value,
            value=float(amount),
            color=CATEGORY_COLORS.get(category, "#C9CBCF"),
            count=count
        ))
    
    # Sort by value descending (largest category first)
    categories.sort(key=lambda x: x.value, reverse=True)
    
    return MonthlyAnalyticsResponse(
        year=target_year,
        month=target_month,
        total_spending=float(total_spending),
        categories=categories,
        transaction_count=transaction_count
    )


@router.get(
    "/summary",
    summary="Get spending summary",
    description="Get overall spending summary for the current user."
)
async def get_spending_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """
    Get a quick spending summary including:
    - Total all-time spending
    - Current month spending
    - Number of expenses
    - Top category
    """
    now = datetime.utcnow()
    
    # Total all-time spending
    total_query = (
        select(func.sum(Expense.amount))
        .where(Expense.user_id == current_user.id)
    )
    total_result = await db.execute(total_query)
    total_all_time = total_result.scalar() or Decimal("0.00")
    
    # Current month spending
    month_query = (
        select(func.sum(Expense.amount))
        .where(Expense.user_id == current_user.id)
        .where(extract("year", Expense.date) == now.year)
        .where(extract("month", Expense.date) == now.month)
    )
    month_result = await db.execute(month_query)
    current_month_spending = month_result.scalar() or Decimal("0.00")
    
    # Transaction count
    count_query = (
        select(func.count(Expense.id))
        .where(Expense.user_id == current_user.id)
    )
    count_result = await db.execute(count_query)
    expense_count = count_result.scalar() or 0
    
    # Top category (by total amount)
    top_category_query = (
        select(Expense.category, func.sum(Expense.amount).label("total"))
        .where(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .limit(1)
    )
    top_result = await db.execute(top_category_query)
    top_row = top_result.first()
    
    top_category = None
    if top_row:
        top_category = {
            "name": top_row.category.value,
            "amount": float(top_row.total)
        }
    
    return {
        "total_all_time": float(total_all_time),
        "current_month_spending": float(current_month_spending),
        "current_month": now.strftime("%B %Y"),
        "expense_count": expense_count,
        "top_category": top_category
    }
