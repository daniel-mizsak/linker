"""
Tests for the delete link endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_delete_link_unauthorized(client: TestClient, slug: str) -> None:
    response = client.delete(f"/api/v1/links/{slug}")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


def test_delete_link_invalid_token(client: TestClient, linker_token: str, slug: str) -> None:
    response = client.delete(f"/api/v1/links/{slug}", headers={"Authorization": f"Bearer {linker_token}_invalid"})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid token"


def test_delete_link_invalid_slug(client: TestClient, auth_headers: dict[str, str], slug_invalid: str) -> None:
    response = client.delete(f"/api/v1/links/{slug_invalid}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug_invalid}' is not valid"


def test_delete_link_slug_not_in_use(client: TestClient, auth_headers: dict[str, str], slug: str) -> None:
    response = client.delete(f"/api/v1/links/{slug}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug}' is not in use"


def test_delete_link(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})

    response = client.delete(f"/api/v1/links/{slug}", headers=auth_headers)

    assert response.status_code == 204

    response = client.get(f"/api/v1/links/{slug}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug}' is not in use"


def test_delete_link_resets_count(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})
    client.get(f"/{slug}", follow_redirects=False)
    client.get(f"/{slug}", follow_redirects=False)

    response = client.get(f"/api/v1/links/{slug}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data["clicks"] == 2

    client.delete(f"/api/v1/links/{slug}", headers=auth_headers)
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": f"{target_url}/1"})

    response = client.get(f"/api/v1/links/{slug}", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data["clicks"] == 0
