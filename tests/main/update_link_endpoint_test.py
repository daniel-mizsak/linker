"""
Tests for the update link endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_update_link_unauthorized(client: TestClient, slug: str) -> None:
    response = client.patch(f"/api/v1/links/{slug}")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


def test_update_link_invalid_token(client: TestClient, linker_token: str, slug: str) -> None:
    response = client.patch(f"/api/v1/links/{slug}", headers={"Authorization": f"Bearer {linker_token}_invalid"})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid token"


def test_update_link_invalid_target_url(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str,
    target_url_invalid: str,
) -> None:
    response = client.patch(f"/api/v1/links/{slug}", headers=auth_headers, json={"target_url": target_url_invalid})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"The provided url '{target_url_invalid}' is not valid"


def test_update_link_invalid_slug(
    client: TestClient,
    auth_headers: dict[str, str],
    slug_invalid: str,
    target_url: str,
) -> None:
    response = client.patch(f"/api/v1/links/{slug_invalid}", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug_invalid}' is not valid"


def test_update_link_slug_not_in_use(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str,
    target_url: str,
) -> None:
    response = client.patch(f"/api/v1/links/{slug}", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug}' is not in use"


def test_update_link_existing_target_url(
    client: TestClient,
    auth_headers: dict[str, str],
    slugs: list[str],
    target_url: str,
) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slugs[0], "target_url": target_url})
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slugs[1], "target_url": f"{target_url}/1"})

    response = client.patch(f"/api/v1/links/{slugs[1]}", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"Link with target url '{target_url}' already exists under slug '{slugs[0]}'"


def test_update_link(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": f"{target_url}/1"})

    response = client.patch(f"/api/v1/links/{slug}", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 200
    assert set(data.keys()) == {"slug", "target_url", "clicks"}
    assert data["slug"] == slug
    assert data["target_url"] == target_url
