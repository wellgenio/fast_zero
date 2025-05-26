from http import HTTPStatus

from tests.conftest import TodoFactory


def test_create_todo(client, token):
    response = client.post(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test todo",
            "description": "Test todo description",
            "state": "draft",
        },
    )
    assert response.json() == {
        "id": 1,
        "title": "Test todo",
        "description": "Test todo description",
        "state": "draft",
    }


def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(expected_todos, user_id=user.id),
    )
    session.commit()

    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == expected_todos


def test_list_todos_filter_title_should_return_5_todos(
    session,
    client,
    user,
    token,
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title="title",
        ),
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title="headline",
        ),
    )
    session.commit()

    response = client.get(
        "/todos/?title=tit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(
    session,
    client,
    user,
    token,
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            description="description",
        ),
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            description="text",
        ),
    )
    session.commit()

    response = client.get(
        "/todos/?description=des",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(
    session,
    client,
    user,
    token,
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            state="draft",
        ),
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            state="done",
        ),
    )
    session.commit()

    response = client.get(
        "/todos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["todos"]) == expected_todos


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "message": "Task has been deleted successfully.",
    }


def test_delete_todo_should_return_404(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        "/todos/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Task not found."


def test_update_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.put(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated title",
            "description": "Updated description",
            "state": "done",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": todo.id,
        "title": "Updated title",
        "description": "Updated description",
        "state": "done",
    }


def test_update_todo_should_return_404(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.put(
        "/todos/999",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated title",
            "description": "Updated description",
            "state": "done",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Task not found."
