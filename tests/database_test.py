"""
Tests for the database.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest

from linker.constants import (
    POSTGRES_DATABASE_KEY,
    POSTGRES_HOST_KEY,
    POSTGRES_PASSWORD_KEY,
    POSTGRES_PORT_KEY,
    POSTGRES_USERNAME_KEY,
)
from linker.database import get_database_url

database_constants = {
    POSTGRES_HOST_KEY: "postgres_host",
    POSTGRES_PORT_KEY: "5432",
    POSTGRES_DATABASE_KEY: "postgres_database",
    POSTGRES_USERNAME_KEY: "postgres_username",
    POSTGRES_PASSWORD_KEY: "postgres_password",
}


@pytest.mark.parametrize(
    "missing_environment_variable",
    [
        POSTGRES_HOST_KEY,
        POSTGRES_PORT_KEY,
        POSTGRES_DATABASE_KEY,
        POSTGRES_USERNAME_KEY,
        POSTGRES_PASSWORD_KEY,
    ],
)
def test_get_database_url_missing_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
    missing_environment_variable: str,
) -> None:
    for key, value in database_constants.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(missing_environment_variable, raising=True)
    with pytest.raises(RuntimeError, match=f"Environment variable '{missing_environment_variable}' is not set"):
        get_database_url()


def test_get_database_url_port_not_digit(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in database_constants.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv(POSTGRES_PORT_KEY, "fivefourthreetwo")
    msg = f"Environment variable '{POSTGRES_PORT_KEY}' must be a number, got 'fivefourthreetwo'"
    with pytest.raises(ValueError, match=msg):
        get_database_url()


def test_get_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in database_constants.items():
        monkeypatch.setenv(key, value)
    url = get_database_url()
    assert url == "postgresql://postgres_username:postgres_password@postgres_host:5432/postgres_database"
