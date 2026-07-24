import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.analysis  # noqa: F401 — register model with Base.metadata
import app.models.user  # noqa: F401 — register model with Base.metadata
from app.core.database import Base, get_db
from app.main import app as fastapi_app


@pytest.fixture()
def db_session():
    """A fresh, empty SQLite database for a single test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    """A FastAPI TestClient wired to the in-memory test database instead of Postgres."""

    def _override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Register and log in a throwaway user, returning ready-to-use auth headers."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "supersecret1"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "supersecret1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
