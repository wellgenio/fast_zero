from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from jwt.exceptions import ExpiredSignatureError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    to_encode.update({"exp": expire})
    secret_key = Settings().SECRET_KEY
    algorithm = Settings().ALGORITHM

    return encode(
        to_encode,
        secret_key,
        algorithm=algorithm,
    )


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(
            token,
            Settings().SECRET_KEY,
            algorithms=[Settings().ALGORITHM],
        )
        username = payload.get("sub")

        if not username:
            raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception
    except DecodeError:
        raise credentials_exception

    db_user = session.scalar(
        select(User).where(User.email == username),
    )

    if not db_user:
        raise credentials_exception

    return db_user
