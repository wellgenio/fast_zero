import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.settings import Settings


@pytest.fixture
def client(session):
    def fake_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = fake_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        Settings().DATABASE_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    session.close()
    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    user_fake = User(
        username="testuser",
        email="testuser@example.com",
        password="password",
    )

    session.add(user_fake)
    session.commit()
    session.refresh(user_fake)

    return user_fake
