"""
BuildOS User Service
Public account status API.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.core.exceptions import UserNotFoundError
from app.database.dependencies import get_db
from app.database.repositories.identity_repository import IdentityRepository
from app.schemas.status import StatusResponse
from app.services.status_service import StatusService

router = APIRouter(
    prefix="/status",
    tags=["Account Status"],
)

current_user_id_dependency = Depends(get_current_user_id)
db_dependency = Depends(get_db)


@router.get(
    "/me",
    response_model=StatusResponse,
)
def get_current_status(
    user_id: UUID = current_user_id_dependency,
    db: Session = db_dependency,
) -> StatusResponse:
    """Return the authenticated user's current account status."""
    service = StatusService(db)
    identities = IdentityRepository(db)

    try:
        user = service.get_status(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
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

    return StatusResponse(
        user_id=str(user.id),
        status=user.status,
        is_active=service.is_active(user.id),
        status_changed_at=service.get_status_changed_at(user.id),
        verification={
            "status": verification_status,
            "level": verification_level,
        },
    )
