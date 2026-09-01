"""
BuildOS User Service
Internal user status endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import verify_internal_service
from app.core.constants import USER_STATUS_DELETED
from app.core.exceptions import UserNotFoundError
from app.database.dependencies import get_db
from app.database.repositories.identity_repository import IdentityRepository
from app.schemas.user import UserStatusResponse
from app.services.status_service import StatusService

router = APIRouter(
    prefix="/users",
    tags=["Internal User Status"],
)


@router.get(
    "/{user_id}/status",
    response_model=UserStatusResponse,
    dependencies=[Depends(verify_internal_service)],
)
def get_user_status(
    user_id: UUID,
    db: Session = Depends(get_db),  # noqa: B008
) -> UserStatusResponse:
    """Return the current status and verification summary for a user."""

    service = StatusService(db)
    identities = IdentityRepository(db)

    try:
        user = service.get_status(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "User not found.",
            },
        ) from exc

    verification_values = [
        identity.is_verified
        for identity in identities.get_by_user_id(user.id)
        if identity.type in {"email", "phone"}
    ]

    if any(verification_values):
        verification_status = "verified"
        verification_level = "contact_verified"
    else:
        verification_status = "unverified"
        verification_level = "none"

    return UserStatusResponse(
        user_id=user.id,
        status=user.status,
        is_active=(
            user.status != USER_STATUS_DELETED
            and service.is_active(user.id)
        ),
        status_changed_at=service.get_status_changed_at(user.id),
        verification={
            "status": verification_status,
            "level": verification_level,
        },
    )
