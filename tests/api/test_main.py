import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.
    """
    return TestClient(app)


def test_app_starts():
    """
    Smoke test to verify that the FastAPI app can start.
    """
    # Simply creating the TestClient will start the app
    client = TestClient(app)
    assert client is not None


def test_api_root(client):
    """
    Test that the API root returns a 200 response.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "SynthDrive RAG Service" in response.text


def test_api_health(client):
    """
    Test that the health endpoint returns a 200 response.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_docs_available(client):
    """
    Test that the API documentation is available.
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()