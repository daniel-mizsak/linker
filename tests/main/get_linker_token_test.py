"""
Tests for getting the linker token.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import pytest

from linker.constants import LINKER_TOKEN_KEY
from linker.main import get_linker_token

linker_constants = {
    LINKER_TOKEN_KEY: "linker_token",
}


def test_get_linker_token_missing_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in linker_constants.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(LINKER_TOKEN_KEY, raising=True)
    with pytest.raises(RuntimeError, match=f"Environment variable '{LINKER_TOKEN_KEY}' is not set"):
        get_linker_token()


def test_get_linker_token(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in linker_constants.items():
        monkeypatch.setenv(key, value)
    token = get_linker_token()
    assert token == "linker_token"  # noqa: S105
