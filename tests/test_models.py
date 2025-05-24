from sqlalchemy import select

from fast_zero.models import User


def test_user_model(session):
    user = User(
        username="testuser",
        email="testuser@example.com",
        password="password123",
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(
            User.email == "testuser@example.com",
        )
    )

    assert result.id == 1
    assert result.created_at is not None
    assert result.username == "testuser"
    assert result.email == "testuser@example.com"
    assert result.password == "password123"
