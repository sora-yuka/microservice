import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas.account import CurrentUser

SECRET_KEY = "django-insecure-k2qsqocbs)8gnc#el=6zd+236@norof*&#9!hrn88#$5^ki0df"

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> CurrentUser:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token"
        )
    return CurrentUser(
        id=payload["user_id"], email=payload["email"], is_staff=payload["is_staff"]
    )


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_staff(user: CurrentUserDep) -> CurrentUserDep:
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required"
        )
    return user
