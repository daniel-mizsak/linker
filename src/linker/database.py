"""
PostgreSQL database connection and session management.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from linker.constants import (
    POSTGRES_DATABASE_KEY,
    POSTGRES_HOST_KEY,
    POSTGRES_PASSWORD_KEY,
    POSTGRES_PORT_KEY,
    POSTGRES_USERNAME_KEY,
)
from linker.models import Link
from linker.slugs import get_slugs


def get_database_url() -> str:
    """Load database connection url from environment variables."""
    postgres_host = os.getenv(POSTGRES_HOST_KEY)
    if postgres_host is None:
        msg = f"Environment variable '{POSTGRES_HOST_KEY}' is not set"
        raise RuntimeError(msg)
    postgres_port = os.getenv(POSTGRES_PORT_KEY)
    if postgres_port is None:
        msg = f"Environment variable '{POSTGRES_PORT_KEY}' is not set"
        raise RuntimeError(msg)
    if not postgres_port.isdigit():
        msg = f"Environment variable '{POSTGRES_PORT_KEY}' must be a number, got '{postgres_port}'"
        raise ValueError(msg)
    postgres_database = os.getenv(POSTGRES_DATABASE_KEY)
    if postgres_database is None:
        msg = f"Environment variable '{POSTGRES_DATABASE_KEY}' is not set"
        raise RuntimeError(msg)
    postgres_username = os.getenv(POSTGRES_USERNAME_KEY)
    if postgres_username is None:
        msg = f"Environment variable '{POSTGRES_USERNAME_KEY}' is not set"
        raise RuntimeError(msg)
    postgres_password = os.getenv(POSTGRES_PASSWORD_KEY)
    if postgres_password is None:
        msg = f"Environment variable '{POSTGRES_PASSWORD_KEY}' is not set"
        raise RuntimeError(msg)

    return f"postgresql://{postgres_username}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}"


def create_db() -> None:
    """Create the database and populate it with initial data."""
    engine = create_engine(get_database_url())
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if not session.exec(select(Link)).first():
            session.add_all([Link(slug=slug) for slug in get_slugs()])
            session.commit()


def get_session() -> Generator[Session, None, None]:
    """Get session for database operations."""
    engine = create_engine(get_database_url())
    with Session(engine) as session:
        yield session
