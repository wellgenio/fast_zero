from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from fast_zero.settings import Settings


def test_get_password_hash_should_return_hashed_password():
    password = "password"
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_verify_password_should_return_true_for_correct_password():
    password = "password"
    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False


def test_create_access_token_should_return_jwt_token():
    data = {"sub": "test_user"}
    token = create_access_token(data)
    secret_key = Settings().SECRET_KEY

    result = decode(token, secret_key, algorithms=[Settings().ALGORITHM])

    assert token is not None
    assert result["sub"] == data["sub"]
    assert result["exp"] is not None


def test_get_current_user_decode_error():
    fake_session = None

    invalid_token = "invalid.jwt.token"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            session=fake_session,
            token=invalid_token,
        )
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_without_username_in_token():
    data = {}
    token = create_access_token(data)

    fake_session = None

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            session=fake_session,
            token=token,
        )
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


def test_get_current_user_user_not_found():
    data = {"sub": "notfound@example.com"}
    token = create_access_token(data)

    class FakeSession:
        @staticmethod
        def scalar(*args, **kwargs):
            return None

    fake_session = FakeSession()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            session=fake_session,
            token=token,
        )
    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"
