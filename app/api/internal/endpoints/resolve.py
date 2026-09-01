"""
BuildOS User Service
Internal identity resolution endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import verify_internal_service
from app.core.constants import USER_STATUS_DELETED
from app.database.dependencies import get_db
from app.schemas.user import (
    ResolvedIdentity,
    UserResolveRequest,
    UserResolveResponse,
)
from app.services.identity_service import IdentityService

router = APIRouter(
    prefix="/users",
    tags=["Internal Identity"],
)


@router.post(
    "/resolve",
    response_model=UserResolveResponse,
    dependencies=[Depends(verify_internal_service)],
)
def resolve_user(
    request: UserResolveRequest,
    db: Session = Depends(get_db),   # noqa: B008
) -> UserResolveResponse:
    """Resolve an email, phone, or username to a canonical user."""

    service = IdentityService(db)

    try:
        user_id, resolved_status, identities = service.resolve(
            request.type,
            request.identifier,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_FAILED",
                "message": str(exc),
            },
        ) from exc

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "IDENTITY_NOT_FOUND",
                "message": "No user found with this identifier",
            },
        )

    if resolved_status == USER_STATUS_DELETED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "code": "USER_DELETED",
                "message": "This user account has been deleted",
            },
        )

    user = service.users.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "IDENTITY_NOT_FOUND",
                "message": "No user found with this identifier",
            },
        )

    return UserResolveResponse(
        user_id=user.id,
        status=user.status,
        identities=[
            ResolvedIdentity(
                type=identity.type,
                value=identity.value,
                is_verified=identity.is_verified,
            )
            for identity in identities
        ],
    )
