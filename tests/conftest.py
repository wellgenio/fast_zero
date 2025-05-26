import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User, table_registry
from fast_zero.scurity import get_password_hash
from fast_zero.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda u: f"{u.username}@example.com")
    password = factory.LazyAttribute(lambda u: f"{u.username}_password")


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


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
    pwd = "password"
    user_fake = UserFactory(password=get_password_hash(pwd))

    user_fake.clean_password = pwd

    session.add(user_fake)
    session.commit()
    session.refresh(user_fake)

    return user_fake


@pytest.fixture
def other_user(session):
    user_fake = UserFactory()

    session.add(user_fake)
    session.commit()
    session.refresh(user_fake)

    return user_fake


@pytest.fixture
def token(client, user):
    response = client.post(
        "auth/token",
        data={
            "username": user.email,
            "password": user.clean_password,
        },
    )

    return response.json()["access_token"]
