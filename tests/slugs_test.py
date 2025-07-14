"""
Tests for the slugs.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from linker.slugs import get_slugs


def test_get_slugs(slugs: list[str]) -> None:
    generated_slugs = get_slugs()

    assert len(generated_slugs) == 150 * 10
    for slug in slugs:
        assert slug in generated_slugs
