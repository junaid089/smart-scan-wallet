"""
Chat Endpoints

Natural language interface for querying expense data.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.chat_service import process_user_query


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about expenses",
        examples=["How much did I spend on food this month?"]
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str = Field(description="Human-friendly answer")
    query: str = Field(default=None, description="Generated SQL query (for debugging)")
    result_count: int = Field(default=0, description="Number of results found")


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat with your expense data",
    description="Ask natural language questions about your expenses and get AI-powered answers."
)
async def chat_with_data(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ChatResponse:
    """
    Natural language interface to query expense data.
    
    Examples:
    - "How much did I spend on Uber?"
    - "What's my total spending this month?"
    - "Show me my food expenses"
    - "Am I spending too much on entertainment?"
    - "What are my subscriptions?"
    
    The AI will:
    1. Convert your question to a SQL query
    2. Execute it against your expenses
    3. Return a friendly, summarized answer
    """
    try:
        result = await process_user_query(
            user_query=request.message,
            user_id=current_user.id,
            session=db
        )
        
        return ChatResponse(
            response=result["response"],
            query=result.get("query"),
            result_count=result.get("result_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get(
    "/suggestions",
    summary="Get chat suggestions",
    description="Get example questions to ask."
)
async def get_chat_suggestions() -> dict:
    """
    Return suggested questions users can ask.
    """
    return {
        "suggestions": [
            "How much did I spend this month?",
            "What's my biggest expense category?",
            "Show me my restaurant expenses",
            "How much did I spend on subscriptions?",
            "What was my spending last month?",
            "Show me expenses over $50",
            "How much did I spend on Uber?",
            "What's my average daily spending?",
        ]
    }
