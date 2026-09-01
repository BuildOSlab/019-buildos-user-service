"""
BuildOS User Service
Internal API Router.
"""

from fastapi import APIRouter

from app.api.internal.endpoints.resolve import router as resolve_router
from app.api.internal.endpoints.status import router as status_router
from app.api.internal.endpoints.users import router as users_router

router = APIRouter()

router.include_router(users_router)
router.include_router(resolve_router)
router.include_router(status_router)
