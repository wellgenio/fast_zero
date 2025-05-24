from jwt import decode

from fast_zero.scurity import (
    create_access_token,
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
