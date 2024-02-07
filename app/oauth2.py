import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.config import IST


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta | None = None, exp_never: bool = False):
    if not exp_never:
        expire = datetime.now(IST) + (
                expires_delta or timedelta(days=int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", 1)))
        )
        data.update({"exp": expire})
    return jwt.encode(
        data, os.environ["SECRET_KEY"], os.getenv("JWT_ALGORITHM", "HS256")
    )


def get_payload(token, invalid_token_exception):
    try:
        return jwt.decode(
            token,
            os.environ["SECRET_KEY"],
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
        )
    except JWTError:
        raise invalid_token_exception


def get_reg_no(token: str, invalid_token_exception):
    payload = get_payload(token, invalid_token_exception)
    return payload["reg_no"]


def get_admin(token: str = Depends(oauth2_scheme)):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token"
    )
    return get_reg_no(token, invalid_token_exception)
