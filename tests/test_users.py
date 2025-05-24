from http import HTTPStatus

from fast_zero.schemas import UserPublicSchema


def test_create_user_should_return_user_with_id(client):
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert "id" in response.json()
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "testuser@example.com"


def test_create_user_should_return_409_if_username_exists(client, user):
    response = client.post(
        "/users/",
        json={
            "username": user.username,
            "email": "teste@gmail.com",
            "password": "password",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["detail"] == "Username already exists"


def test_create_user_should_return_409_if_email_exists(client, user):
    response = client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": user.email,
            "password": "password",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()["detail"] == "Email already exists"


def test_read_users_should_return_list_of_users(client, user):
    user_schema = UserPublicSchema.model_validate(user).model_dump()

    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user_should_return_updated_user(client, user, token):
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "newpassword",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "updateduser",
        "email": "updateduser@example.com",
    }


def test_update_user_should_return_404_if_user_not_is_current_user(
    client,
    token,
):
    response = client.put(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "password": "newpassword",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user_should_return_204_if_user_exists(client, user, token):
    response = client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""


def test_delete_user_should_return_404_if_user_not_is_current_user(
    client,
    token,
):
    response = client.delete(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
