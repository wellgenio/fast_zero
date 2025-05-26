from http import HTTPStatus

from freezegun import freeze_time


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


def test_token_expired_after_time(client, user):
    with freeze_time("2025-01-01 12:00:00"):
        # Generate a token
        response = client.post(
            "auth/token",
            data={
                "username": user.email,
                "password": user.clean_password,
            },
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()["access_token"]

    with freeze_time("2025-01-01 12:31:00"):
        # Attempt to access a protected endpoint with the expired token
        response = client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "New Name",
                "email": "new_email@example.com",
                "password": "new_password",
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"


def test_token_token(client, token):
    response = client.get(
        "auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert "token_type" in token
    assert token["token_type"] == "Bearer"


def test_token_expired_dont_refresh(client, user):
    with freeze_time("2025-01-01 12:00:00"):
        # Generate a token
        response = client.post(
            "auth/token",
            data={
                "username": user.email,
                "password": user.clean_password,
            },
        )

    assert response.status_code == HTTPStatus.OK
    token = response.json()["access_token"]

    with freeze_time("2025-01-01 12:31:00"):
        # Attempt to access a protected endpoint with the expired token
        response = client.get(
            "auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == "Could not validate credentials"
