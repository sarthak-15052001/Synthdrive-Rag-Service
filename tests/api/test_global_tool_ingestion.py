import pytest
from datetime import datetime, timezone
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from httpx import HTTPStatusError, RequestError
from src.main import app
from src.data_stores.global_tools_client import GlobalToolsClient

client = TestClient(app)

def test_ingest_global_tool_success():
    """Test successful ingestion of a global tool with the new payload structure"""
    payload = {
        "name": "Test AI Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com", "https://source2.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": ["Content Generation", "Marketing"]
        },
        "short_description": "A test AI tool for writing",
        "detailed_description": "This is a detailed description of the test AI tool...",
        "features": [
            {
                "name": "Feature 1",
                "description": "Description of feature 1",
                "use_case": "Example use case for feature 1"
            }
        ],
        "differentiators": [
            "Unique feature 1",
            "Unique feature 2"
        ],
        "subscriptions": [
            {
                "plan_name": "Free",
                "price_monthly": None,
                "price_annual": None,
                "pricing_model": "freemium",
                "features_included": ["Basic feature 1", "Basic feature 2"]
            }
        ],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": ["EU", "US"],
            "certifications": ["SOC2"]
        },
        "documentation_links": [
            "https://docs.test-tool.com/getting-started"
        ],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": ["AI", "Writing"]
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_ingest_global_tool_missing_required():
    """Test validation of required fields"""
    # Missing name
    payload = {
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": []
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [],
        "differentiators": [],
        "subscriptions": [],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": [],
            "certifications": []
        },
        "documentation_links": [],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": []
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 400
    assert "Tool name is required" in response.json()["detail"]

def test_ingest_global_tool_invalid_url():
    """Test validation of URL fields"""
    payload = {
        "name": "Test Tool",
        "homepage_url": "invalid-url",  # Invalid URL
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": []
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [],
        "differentiators": [],
        "subscriptions": [],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": [],
            "certifications": []
        },
        "documentation_links": [],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": []
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 400
    assert "Invalid URL format" in response.json()["detail"]

def test_ingest_global_tool_invalid_rating():
    """Test validation of rating range"""
    payload = {
        "name": "Test Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": []
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [],
        "differentiators": [],
        "subscriptions": [],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": [],
            "certifications": []
        },
        "documentation_links": [],
        "rating": 6.0,  # Invalid rating > 5
        "logo_url": "https://test-tool.com/logo.png",
        "tags": []
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 400
    assert "Rating must be between 0 and 5" in response.json()["detail"]

@pytest.mark.asyncio
@patch('src.data_stores.global_tools_client.GlobalToolsClient.add_global_tool')
async def test_ingest_global_tool_connector_success(mock_add_global_tool):
    """Test successful integration with global tools connector"""
    # Setup mock
    mock_add_global_tool.return_value = {"status": "success"}
    
    payload = {
        "name": "Test AI Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": ["Content Generation"]
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [
            {
                "name": "Feature 1",
                "description": "Description",
                "use_case": "Use case"
            }
        ],
        "differentiators": ["Unique 1"],
        "subscriptions": [
            {
                "plan_name": "Free",
                "price_monthly": None,
                "price_annual": None,
                "pricing_model": "freemium",
                "features_included": ["Basic"]
            }
        ],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": ["EU"],
            "certifications": ["SOC2"]
        },
        "documentation_links": ["https://docs.test-tool.com"],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": ["AI"]
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 200
    assert "job_id" in response.json()
    mock_add_global_tool.assert_called_once()

@pytest.mark.asyncio
@patch('src.data_stores.global_tools_client.GlobalToolsClient.add_global_tool')
async def test_ingest_global_tool_connector_http_error(mock_add_global_tool):
    """Test handling of HTTP errors from global tools service"""
    # Setup mock to raise HTTPStatusError
    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.text = "Service temporarily unavailable"
    mock_add_global_tool.side_effect = HTTPStatusError(
        "Service unavailable",
        request=Mock(),
        response=mock_response
    )
    
    payload = {
        "name": "Test AI Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": []
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [],
        "differentiators": [],
        "subscriptions": [],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": [],
            "certifications": []
        },
        "documentation_links": [],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": []
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 503
    assert "Service temporarily unavailable" in response.json()["detail"]

@pytest.mark.asyncio
@patch('src.data_stores.global_tools_client.GlobalToolsClient.add_global_tool')
async def test_ingest_global_tool_connector_network_error(mock_add_global_tool):
    """Test handling of network errors when connecting to global tools service"""
    # Setup mock to raise RequestError
    mock_add_global_tool.side_effect = RequestError("Connection failed", request=Mock())
    
    payload = {
        "name": "Test AI Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": []
        },
        "short_description": "A test AI tool",
        "detailed_description": "Description...",
        "features": [],
        "differentiators": [],
        "subscriptions": [],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": [],
            "certifications": []
        },
        "documentation_links": [],
        "rating": 4.5,
        "logo_url": "https://test-tool.com/logo.png",
        "tags": []
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 503
    assert "Global tools service is unavailable" in response.json()["detail"]

def test_ingest_global_tool_without_logo():
    """Test successful ingestion of a global tool without logo_url"""
    payload = {
        "name": "Test AI Tool",
        "homepage_url": "https://test-tool.com",
        "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": ["https://source1.com", "https://source2.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": ["Content Generation", "Marketing"]
        },
        "short_description": "A test AI tool for writing",
        "detailed_description": "This is a detailed description of the test AI tool...",
        "features": [
            {
                "name": "Feature 1",
                "description": "Description of feature 1",
                "use_case": "Example use case for feature 1"
            }
        ],
        "differentiators": [
            "Unique feature 1",
            "Unique feature 2"
        ],
        "subscriptions": [
            {
                "plan_name": "Free",
                "price_monthly": None,
                "price_annual": None,
                "pricing_model": "freemium",
                "features_included": ["Basic feature 1", "Basic feature 2"]
            }
        ],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": ["EU", "US"],
            "certifications": ["SOC2"]
        },
        "documentation_links": [
            "https://docs.test-tool.com/getting-started"
        ],
        "rating": 4.5,
        "tags": ["AI", "Writing"]
    }

    response = client.post("/api/v1/rag/ingest/global/tool", json=payload)
    assert response.status_code == 200
    assert "job_id" in response.json()