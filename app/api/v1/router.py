"""
BuildOS User Service
Version 1 API Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints.preferences import router as preferences_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.status import router as status_router
from app.api.v1.endpoints.users import router as users_router

router = APIRouter()

router.include_router(users_router)
router.include_router(profiles_router)
router.include_router(preferences_router)
router.include_router(status_router)