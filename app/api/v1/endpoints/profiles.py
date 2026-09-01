"""
BuildOS User Service
Public profile API.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.core.exceptions import (
    ProfileUpdateError,
    UserNotFoundError,
)
from app.database.dependencies import get_db
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.profile_service import ProfileService

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)

current_user_id_dependency = Depends(get_current_user_id)
db_dependency = Depends(get_db)


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_current_profile(
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> ProfileResponse:
    """Return the authenticated user's profile."""
    service = ProfileService(db)

    try:
        profile = service.get_profile(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except ProfileUpdateError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile does not exist.",
        ) from exc

    return ProfileResponse.model_validate(profile)


@router.patch(
    "/me",
    response_model=ProfileResponse,
)
def update_current_profile(
    request: ProfileUpdateRequest,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> ProfileResponse:
    """Update the authenticated user's profile."""
    service = ProfileService(db)

    try:
        profile = service.update_profile(
            user_id=user_id,
            request=request,
        )
        db.commit()
        db.refresh(profile)
    except UserNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except ProfileUpdateError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise

    return ProfileResponse.model_validate(profile)
