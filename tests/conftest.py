"""
Fixtures used in tests.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from linker.database import get_session
from linker.main import app, get_linker_token
from linker.models import Link


@pytest.fixture(name="linker_token")
def linker_token_fixture() -> str:
    return "secret"


@pytest.fixture(name="session")
def session_fixture(slugs: list[str]) -> Iterator[Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([Link(slug=slug) for slug in slugs])
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, linker_token: str) -> Iterator[TestClient]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_linker_token] = lambda: linker_token
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(linker_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {linker_token}"}


@pytest.fixture(name="target_url")
def target_url_fixture() -> str:
    """Default target url."""
    return "https://example.com"


@pytest.fixture(name="target_url_invalid")
def target_url_invalid_fixture() -> str:
    """Invalid target url."""
    return "example.com"


@pytest.fixture(name="slugs")
def slugs_fixture() -> list[str]:
    """List of allowed slugs."""
    return ["bored-bulbasaur", "happy-charmander", "sleepy-squirtle", "surprised-pikachu"]


@pytest.fixture(name="slug")
def slug_fixture() -> str:
    """Default slug."""
    return "surprised-pikachu"


@pytest.fixture(name="slug_invalid")
def slug_invalid_fixture() -> str:
    """Invalid slug."""
    return "surprised-pika"
