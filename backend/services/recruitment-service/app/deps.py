from uuid import UUID

from fastapi import Header, HTTPException, status

from app.schemas import CurrentUserContext


def get_current_user_context(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_auth_id: str | None = Header(default=None, alias="X-Auth-Id"),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> CurrentUserContext:
    if not all([x_user_id, x_auth_id, x_user_email, x_user_role]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing gateway authentication headers",
        )

    try:
        return CurrentUserContext(
            user_id=UUID(x_user_id),
            auth_id=UUID(x_auth_id),
            email=x_user_email,
            role=x_user_role,
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid gateway authentication headers",
        ) from err
