"""
Tests for the forward to target url endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_forward_to_target_url_invalid_slug(client: TestClient, slug_invalid: str) -> None:
    response = client.get(f"/{slug_invalid}", follow_redirects=False)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug_invalid}' is not valid"


def test_forward_to_target_url_slug_not_in_use(client: TestClient, slug: str) -> None:
    response = client.get(f"/{slug}", follow_redirects=False)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug}' is not in use"


def test_forward_to_target_url(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})

    response = client.get(f"/{slug}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == target_url

    client.get(f"/{slug}", follow_redirects=False)
    client.get(f"/{slug}", follow_redirects=False)

    response = client.get(f"/api/v1/links/{slug}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data["slug"] == slug
    assert data["target_url"] == target_url
    assert data["clicks"] == 3
