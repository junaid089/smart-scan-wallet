"""
API V1 Router

Combines all endpoint routers under the /api/v1 prefix.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, receipts, analytics, chat


api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(auth.router)

# Include receipt endpoints
api_router.include_router(receipts.router)

# Include analytics endpoints
api_router.include_router(analytics.router)

# Include chat endpoints
api_router.include_router(chat.router)
