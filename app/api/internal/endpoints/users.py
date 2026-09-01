"""
BuildOS User Service
Internal user endpoints.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import verify_internal_service
from app.core.exceptions import IdentityAlreadyExistsError
from app.database.dependencies import get_db
from app.schemas.user import UserCreateRequest, UserCreateResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Internal Users"],
)


@router.post(
    "/create",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_internal_service)],
)
def create_user(
    request: UserCreateRequest,
    db: Session = Depends(get_db),   # noqa: B008
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
) -> UserCreateResponse:
    """Create or safely retry a canonical user for the Auth Service."""

    normalized_idempotency_key = idempotency_key.strip()

    if not normalized_idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_IDEMPOTENCY_KEY",
                "message": "Idempotency-Key must not be empty.",
            },
        )

    service = UserService(db)

    try:
        user = service.create_user(
            request,
            idempotency_key=normalized_idempotency_key,
        )

        db.commit()
        db.refresh(user)

    except IdentityAlreadyExistsError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "IDENTITY_ALREADY_EXISTS",
                "message": str(exc),
            },
        ) from exc

    except ValueError as exc:
        db.rollback()

        if str(exc) == "At least one identity is required.":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "IDENTITY_REQUIRED",
                    "message": str(exc),
                },
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "IDEMPOTENCY_CONFLICT",
                "message": str(exc),
            },
        ) from exc

    except IntegrityError:
        db.rollback()

        # A concurrent request may have won the unique idempotency-key
        # race. Retry through the service so it verifies the stored
        # idempotency hash before returning the existing user.
        try:
            user = service.create_user(
                request,
                idempotency_key=normalized_idempotency_key,
            )

            db.commit()
            db.refresh(user)

        except IdentityAlreadyExistsError as retry_exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "IDENTITY_ALREADY_EXISTS",
                    "message": str(retry_exc),
                },
            ) from retry_exc

        except ValueError as retry_exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "IDEMPOTENCY_CONFLICT",
                    "message": str(retry_exc),
                },
            ) from retry_exc

        except IntegrityError as retry_exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "REGISTRATION_FAILED",
                    "message": "Unable to create user.",
                },
            ) from retry_exc

        except Exception:
            db.rollback()
            raise

    except Exception:
        db.rollback()
        raise

    return UserCreateResponse(
        user_id=user.id,
        public_id=user.public_id,
        status=user.status,
        created_at=user.created_at,
    )
