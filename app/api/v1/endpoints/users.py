"""
BuildOS User Service
Public user API.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.core.exceptions import UserNotFoundError
from app.database.dependencies import get_db
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

# Module-level dependency singletons.
# This avoids Ruff B008 while preserving FastAPI dependency injection.
current_user_id_dependency = Depends(get_current_user_id)
db_dependency = Depends(get_db)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user(
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> UserResponse:
    """Return the authenticated user's account."""
    service = UserService(db)

    try:
        user = service.get_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc

    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_current_user(
    request: UserUpdateRequest,
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> UserResponse:
    """Update allowed fields on the authenticated user's account."""
    service = UserService(db)

    try:
        user = service.update_display_name(
            user_id=user_id,
            display_name=request.display_name,
        )
        db.commit()
        db.refresh(user)
    except UserNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return UserResponse.model_validate(user)

