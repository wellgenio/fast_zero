import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry
from fast_zero.settings import Settings


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine(Settings().DATABASE_TEST_URL)
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    session.close()
    table_registry.metadata.drop_all(engine)
