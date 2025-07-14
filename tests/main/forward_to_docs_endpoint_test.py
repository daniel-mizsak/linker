"""
Test for the forward to docs endpoint.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from fastapi.testclient import TestClient


def test_forward_to_docs(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["Location"] == "/docs"
