"""
API Dependencies

Reusable dependency injection functions for FastAPI endpoints.
Includes database session and authentication dependencies.
"""
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.database import async_session_factory
from app.models.user import User


# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.
    
    Yields an async database session and ensures proper cleanup.
    Use this as a dependency in route handlers.
    
    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Decodes and validates the JWT token
    3. Retrieves the user from the database
    4. Returns the User object if valid
    
    Args:
        token: JWT token extracted from Authorization header
        db: Database session
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extract user email from token subject
    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Query the database for the user
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Get the current active user.
    
    This dependency builds on get_current_user and additionally
    verifies that the user account is active.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        The authenticated and active User object
        
    Raises:
        HTTPException: 403 Forbidden if user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


# Type aliases for cleaner route signatures
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]
