"""
Tests for the create link endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_create_link_unauthorized(client: TestClient) -> None:
    response = client.post("/api/v1/links")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


def test_create_link_invalid_token(client: TestClient, linker_token: str) -> None:
    response = client.post("/api/v1/links", headers={"Authorization": f"Bearer {linker_token}_invalid"})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid token"


def test_create_link_invalid_target_url(
    client: TestClient,
    auth_headers: dict[str, str],
    target_url_invalid: str,
) -> None:
    response = client.post("/api/v1/links", headers=auth_headers, json={"target_url": target_url_invalid})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"The provided url '{target_url_invalid}' is not valid"


# TODO: Rename tests to match the name of the exception.
def test_create_link_existing_target_url(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str,
    target_url: str,
) -> None:
    # We specify slug here to compare it against in the error message.
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})

    response = client.post("/api/v1/links", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"Link with target url '{target_url}' already exists under slug '{slug}'"


def test_create_link_no_available_slugs(
    client: TestClient,
    auth_headers: dict[str, str],
    target_url: str,
    slugs: list[str],
) -> None:
    for index in range(len(slugs)):
        client.post(
            "/api/v1/links",
            headers=auth_headers,
            json={"target_url": f"{target_url}/{index + 1}"},  # Create valid target urls to exhaust all slugs.
        )

    response = client.post("/api/v1/links", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == "No unused slugs are available in the database"


def test_create_link_invalid_slug(
    client: TestClient,
    auth_headers: dict[str, str],
    slug_invalid: str,
    target_url: str,
) -> None:
    response = client.post("/api/v1/links", headers=auth_headers, json={"slug": slug_invalid, "target_url": target_url})
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"Slug '{slug_invalid}' is not valid"


def test_create_link_existing_slug(
    client: TestClient,
    auth_headers: dict[str, str],
    slug: str,
    target_url: str,
) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})

    response = client.post(
        "/api/v1/links",
        headers=auth_headers,
        json={"slug": slug, "target_url": f"{target_url}/1"},
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"] == f"Slug '{slug}' is already in use for target url '{target_url}'"


def test_create_link_no_slug(
    client: TestClient,
    auth_headers: dict[str, str],
    target_url: str,
    slugs: list[str],
) -> None:
    response = client.post("/api/v1/links", headers=auth_headers, json={"target_url": target_url})
    data = response.json()

    assert response.status_code == 200
    assert data["slug"] in slugs
    assert data["target_url"] == target_url
    assert data["clicks"] == 0


def test_create_link(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    response = client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})
    data = response.json()

    assert response.status_code == 200
    assert set(data.keys()) == {"slug", "target_url", "clicks"}
    assert data["slug"] == slug
    assert data["target_url"] == target_url
    assert data["clicks"] == 0
