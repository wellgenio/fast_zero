from http import HTTPStatus


def test_get_token_should_return_jwt_token(client, user):
    response = client.post(
        "auth/token",
        data={
            "username": user.email,
            "password": user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_get_token_should_return_401_if_invalid_credentials(client):
    response = client.post(
        "auth/token",
        data={
            "username": "invaliduser",
            "password": "invalidpassword",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"
