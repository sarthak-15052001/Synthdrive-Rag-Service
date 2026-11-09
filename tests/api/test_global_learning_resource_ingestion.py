import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.global_tools_client import GlobalLearningResourcesClient

@pytest.fixture(autouse=True)
def setup_app():
    """Setup test app with dummy postgres client"""
    class DummyPostgresClient:
        def add_document(self, *args, **kwargs): pass
        def get_document_by_id(self, *args, **kwargs): return None
        def search_documents(self, *args, **kwargs): return []
        def delete_document(self, *args, **kwargs): return False
        def close(self): pass
    
    app.state.postgres_client = DummyPostgresClient()
    yield
    if hasattr(app.state, "postgres_client"):
        app.state.postgres_client.close()

client = TestClient(app)

@pytest.fixture
def mock_learning_resources_client():
    with patch('src.api.v1.endpoints.ingest.GlobalLearningResourcesClient') as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance
        yield instance

def test_ingest_global_learning_resource_success(mock_learning_resources_client):
    """Test successful ingestion of a global learning resource with the new payload structure"""
    payload = {
        "title": "Introduction to AI Ethics",
        "description": "A comprehensive guide to ethical considerations in artificial intelligence development",
        "source_url": "https://example.com/ai-ethics-guide",
        "resource_type": "article",
        "categories": {
            "primary": "AI Ethics",
            "secondary": ["Responsible AI", "AI Governance"]
        },
        "topics_discussed": ["Bias in AI", "Transparency", "Accountability", "Privacy"],
        "target_audience": {
            "expertise_level": "intermediate",
            "job_roles": ["Data Scientist", "AI Engineer", "Product Manager"]
        },
        "useful_context": ["AI Development", "Policy Creation", "Team Training"],
        "content": {
            "summary": "This article provides a comprehensive overview of ethical considerations in AI development, including bias mitigation, transparency requirements, and governance frameworks.",
            "full_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...",
            "video_transcript": None,
            "video_url": None,
            "image_analysis": [
                {
                    "image_url": "https://example.com/images/ai-ethics-diagram.png",
                    "description": "Diagram showing the relationship between various ethical considerations in AI development"
                }
            ]
        },
        "tags": ["ethics", "ai", "governance", "bias", "transparency"],
        "estimatedTime": "15 minutes",
        "last_scraped_at": datetime.now(timezone.utc).isoformat()
    }

    # Configure mock to return success
    mock_learning_resources_client.post_learning_resource.return_value = {"status": "success"}
    
    response = client.post("/api/v1/rag/ingest/global/learning-resource", json=payload)
    
    # Verify the connector was called with correct data
    mock_learning_resources_client.post_learning_resource.assert_called_once()
    called_resource = mock_learning_resources_client.post_learning_resource.call_args[0][0]
    assert called_resource.title == payload["title"]
    assert called_resource.description == payload["description"]
    assert str(called_resource.source_url) == payload["source_url"]
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_ingest_global_learning_resource_missing_required():
    """Test validation of required fields"""
    # Missing title
    payload = {
        "description": "A comprehensive guide",
        "source_url": "https://example.com/guide",
        "resource_type": "article",
        "categories": {
            "primary": "AI Ethics",
            "secondary": []
        },
        "topics_discussed": ["Ethics"],
        "target_audience": {
            "expertise_level": "beginner",
            "job_roles": ["Developer"]
        },
        "useful_context": ["Development"],
        "content": {
            "summary": "A guide about AI",
            "full_text": "Content here..."
        },
        "tags": ["ai"],
        "estimatedTime": "10 minutes",
        "last_scraped_at": datetime.now(timezone.utc).isoformat()
    }

    response = client.post("/api/v1/rag/ingest/global/learning-resource", json=payload)
    assert response.status_code == 400
    assert "Title is required" in response.json()["detail"]

def test_ingest_global_learning_resource_invalid_url():
    """Test validation of URL fields"""
    payload = {
        "title": "Test Resource",
        "description": "A test resource",
        "source_url": "invalid-url",  # Invalid URL
        "resource_type": "article",
        "categories": {
            "primary": "AI Ethics",
            "secondary": []
        },
        "topics_discussed": ["Ethics"],
        "target_audience": {
            "expertise_level": "beginner",
            "job_roles": ["Developer"]
        },
        "useful_context": ["Development"],
        "content": {
            "summary": "A guide about AI",
            "full_text": "Content here...",
            "image_analysis": [
                {
                    "image_url": "also-invalid-url",  # Invalid URL
                    "description": "Test image"
                }
            ]
        },
        "tags": ["ai"],
        "estimatedTime": "10 minutes",
        "last_scraped_at": datetime.now(timezone.utc).isoformat()
    }

    response = client.post("/api/v1/rag/ingest/global/learning-resource", json=payload)
    assert response.status_code == 400
    assert "Invalid URL format" in response.json()["detail"]

def test_ingest_global_learning_resource_invalid_date():
    """Test validation of date format"""
    payload = {
        "title": "Test Resource",
        "description": "A test resource",
        "source_url": "https://example.com/test",
        "resource_type": "article",
        "categories": {
            "primary": "AI Ethics",
            "secondary": []
        },
        "topics_discussed": ["Ethics"],
        "target_audience": {
            "expertise_level": "beginner",
            "job_roles": ["Developer"]
        },
        "useful_context": ["Development"],
        "content": {
            "summary": "A guide about AI",
            "full_text": "Content here..."
        },
        "tags": ["ai"],
        "estimatedTime": "10 minutes",
        "last_scraped_at": "invalid-date"  # Invalid date format
    }

    response = client.post("/api/v1/rag/ingest/global/learning-resource", json=payload)
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]

def test_ingest_global_learning_resource_connector_failure(mock_learning_resources_client):
    """Test handling of connector failures"""
    payload = {
        "title": "Test Resource",
        "description": "A test resource",
        "source_url": "https://example.com/test",
        "resource_type": "article",
        "categories": {
            "primary": "AI Ethics",
            "secondary": []
        },
        "topics_discussed": ["Ethics"],
        "target_audience": {
            "expertise_level": "beginner",
            "job_roles": ["Developer"]
        },
        "useful_context": ["Development"],
        "content": {
            "summary": "A guide about AI",
            "full_text": "Content here..."
        },
        "tags": ["ai"],
        "estimatedTime": "10 minutes",
        "last_scraped_at": datetime.now(timezone.utc).isoformat()
    }

    # Configure mock to raise an exception
    mock_learning_resources_client.post_learning_resource.side_effect = Exception("Connector error")

    response = client.post("/api/v1/rag/ingest/global/learning-resource", json=payload)
    assert response.status_code == 500
    assert "Error processing learning resource in global service" in response.json()["detail"]