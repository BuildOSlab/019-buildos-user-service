"""
BuildOS User Service
Public preference API.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.core.exceptions import UserNotFoundError
from app.database.dependencies import get_db
from app.schemas.preferences import (
    PreferenceCreateRequest,
    PreferenceResponse,
    PreferenceUpdateRequest,
)
from app.services.preference_service import PreferenceService

router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"],
)

current_user_id_dependency = Depends(get_current_user_id)
db_dependency = Depends(get_db)


@router.get(
    "",
    response_model=list[PreferenceResponse],
)
def list_current_preferences(
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> list[PreferenceResponse]:
    """Return all preferences belonging to the authenticated user."""
    service = PreferenceService(db)

    try:
        preferences = service.list_preferences(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc

    return [
        PreferenceResponse.model_validate(preference)
        for preference in preferences
    ]


@router.get(
    "/{key}",
    response_model=PreferenceResponse,
)
def get_current_preference(
    key: str,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> PreferenceResponse:
    """Return one preference belonging to the authenticated user."""
    service = PreferenceService(db)

    try:
        preference = service.get_preference(
            user_id=user_id,
            key=key,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found.",
        )

    return PreferenceResponse.model_validate(preference)


@router.put(
    "/{key}",
    response_model=PreferenceResponse,
)
def update_current_preference(
    key: str,
    request: PreferenceUpdateRequest,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> PreferenceResponse:
    """Update an existing preference."""
    service = PreferenceService(db)

    try:
        preference = service.update(
            user_id=user_id,
            key=key,
            request=request,
        )
        db.commit()
        db.refresh(preference)
    except UserNotFoundError as exc:
        db.rollback()

        if str(exc) == "Preference not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preference not found.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return PreferenceResponse.model_validate(preference)


@router.post(
    "",
    response_model=PreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_or_update_current_preference(
    request: PreferenceCreateRequest,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> PreferenceResponse:
    """Create or replace a preference."""
    service = PreferenceService(db)

    try:
        preference = service.create_or_update(
            user_id=user_id,
            request=request,
        )
        db.commit()
        db.refresh(preference)
    except UserNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return PreferenceResponse.model_validate(preference)


@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_current_preference(
    key: str,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> None:
    """Delete a preference belonging to the authenticated user."""
    service = PreferenceService(db)

    try:
        deleted = service.delete(
            user_id=user_id,
            key=key,
        )
        db.commit()
    except UserNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except Exception:
        db.rollback()
        raise

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found.",
        )
    