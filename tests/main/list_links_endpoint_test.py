"""
Tests for the list links endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_list_links_unauthorized(client: TestClient) -> None:
    response = client.get("/api/v1/links")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


def test_list_links_invalid_token(client: TestClient, linker_token: str) -> None:
    response = client.get("/api/v1/links", headers={"Authorization": f"Bearer {linker_token}_invalid"})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid token"


def test_list_links_empty(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/links", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data == []


def test_list_links(client: TestClient, auth_headers: dict[str, str], target_url: str, slugs: list[str]) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"target_url": f"{target_url}/1"})
    client.post("/api/v1/links", headers=auth_headers, json={"target_url": f"{target_url}/2"})

    response = client.get("/api/v1/links", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    returned_targets = {item["target_url"] for item in data}
    expected_targets = {f"{target_url}/1", f"{target_url}/2"}
    assert returned_targets == expected_targets
    for item in data:
        assert set(item.keys()) == {"slug", "target_url", "clicks"}
        assert item["slug"] in slugs
