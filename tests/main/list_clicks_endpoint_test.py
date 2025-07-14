"""
Tests for the list clicks endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def test_list_clicks_unauthorized(client: TestClient, slug: str) -> None:
    response = client.get(f"/api/v1/links/{slug}/clicks")
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


def test_list_clicks_invalid_token(client: TestClient, linker_token: str, slug: str) -> None:
    response = client.get(f"/api/v1/links/{slug}/clicks", headers={"Authorization": f"Bearer {linker_token}_invalid"})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Invalid token"


def test_list_clicks_invalid_slug(client: TestClient, auth_headers: dict[str, str], slug_invalid: str) -> None:
    response = client.get(f"/api/v1/links/{slug_invalid}/clicks", headers=auth_headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug_invalid}' is not valid"


def test_list_clicks_slug_not_in_use(client: TestClient, auth_headers: dict[str, str], slug: str) -> None:
    response = client.get(f"/api/v1/links/{slug}/clicks", headers=auth_headers)
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == f"Slug '{slug}' is not in use"


def test_list_clicks_empty(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})

    response = client.get(f"/api/v1/links/{slug}/clicks", headers=auth_headers)
    data = response.json()

    assert response.status_code == 200
    assert data == []


def test_list_clicks(client: TestClient, auth_headers: dict[str, str], slug: str, target_url: str) -> None:
    timestamp = datetime.now(tz=UTC)
    client.post("/api/v1/links", headers=auth_headers, json={"slug": slug, "target_url": target_url})
    client.get(f"/{slug}", follow_redirects=False)
    client.get(f"/{slug}", follow_redirects=False)

    response = client.get(f"/api/v1/links/{slug}/clicks", headers=auth_headers)
    data = response.json()

    timestamps = [item["timestamp"] for item in data]
    assert timestamps == sorted(timestamps, reverse=True)
    assert response.status_code == 200
    assert len(data) == 2
    for item in data:
        item_timestamp = datetime.fromisoformat(item["timestamp"]).replace(tzinfo=UTC)
        assert timestamp < item_timestamp < timestamp + timedelta(seconds=1)
        assert item["ip_address"] == "testclient"
        assert set(item.keys()) == {"ip_address", "timestamp"}
