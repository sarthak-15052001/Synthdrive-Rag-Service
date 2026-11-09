import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.main import app
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.tenant_files_search import TenantUploadedFilesSearchTool
from src.api.dependencies import get_weaviate_client, get_current_user, get_ingestion_graph
from src.ingestion.graph import IngestionGraph

# Mock data for testing
MOCK_FILE_DATA = {
    "file_id": "test-file-id-1",
    "file_name": "test_document.pdf",
    "file_path": "gs://tenant-files/test-org/test_document.pdf",
    "content_chunk": "This is a test document containing financial information for Q3 2023.",
    "organization_id": "test-org",
    "upload_date": "2023-10-15T12:00:00Z",
    "file_type": ".pdf",
    "tags": ["financial", "2023", "Q3"],
    "relevance_score": 0.95,
    "citation_id": "file-1"
}

MOCK_SEARCH_RESULTS = [
    MOCK_FILE_DATA,
    {
        "file_id": "test-file-id-2",
        "file_name": "annual_report_2023.pdf",
        "file_path": "gs://tenant-files/test-org/annual_report_2023.pdf",
        "content_chunk": "Annual financial report for fiscal year 2023. Revenue increased by 15% compared to 2022.",
        "organization_id": "test-org",
        "upload_date": "2023-12-31T10:30:00Z",
        "file_type": ".pdf",
        "tags": ["financial", "2023", "annual"],
        "relevance_score": 0.85,
        "citation_id": "file-2"
    }
]

# Create a test client with overridden dependencies
client = TestClient(app)

# Create a mock for TenantUploadedFilesSearchTool
mock_tenant_files_tool = MagicMock(spec=TenantUploadedFilesSearchTool)
# Configure the mock to return our test data
mock_tenant_files_tool.return_value.search_tenant_files.return_value = MOCK_SEARCH_RESULTS
mock_tenant_files_tool.return_value.get_file_by_id.return_value = MOCK_FILE_DATA

# Save the original class for cleanup
original_tool = TenantUploadedFilesSearchTool

# Replace the class with our mock
TenantUploadedFilesSearchTool = mock_tenant_files_tool

# Create a mock for the current user
mock_current_user = MagicMock()
mock_current_user.return_value = {"username": "testuser"}

# Create a mock for the ingestion graph
mock_ingestion_graph = MagicMock(spec=IngestionGraph)
mock_ingestion_graph.return_value.ingest_document_async.return_value = None  # Successful result

# Create a mock for the Weaviate client
mock_weaviate_client = MagicMock(spec=WeaviateClient)

# Apply the overrides
app.dependency_overrides[get_current_user] = mock_current_user
app.dependency_overrides[get_weaviate_client] = mock_weaviate_client
app.dependency_overrides[get_ingestion_graph] = mock_ingestion_graph

# Mock data for testing
MOCK_FILE_DATA = {
    "file_id": "test-file-id-1",
    "file_name": "test_document.pdf",
    "file_path": "gs://tenant-files/test-org/test_document.pdf",
    "content_chunk": "This is a test document containing financial information for Q3 2023.",
    "organization_id": "test-org",
    "upload_date": "2023-10-15T12:00:00Z",
    "file_type": ".pdf",
    "tags": ["financial", "2023", "Q3"],
    "relevance_score": 0.95,
    "citation_id": "file-1"
}

MOCK_SEARCH_RESULTS = [
    MOCK_FILE_DATA,
    {
        "file_id": "test-file-id-2",
        "file_name": "annual_report_2023.pdf",
        "file_path": "gs://tenant-files/test-org/annual_report_2023.pdf",
        "content_chunk": "Annual financial report for fiscal year 2023. Revenue increased by 15% compared to 2022.",
        "organization_id": "test-org",
        "upload_date": "2023-12-31T10:30:00Z",
        "file_type": ".pdf",
        "tags": ["financial", "2023", "annual"],
        "relevance_score": 0.85,
        "citation_id": "file-2"
    }
]

# Simplified fixtures
@pytest.fixture
def mock_auth():
    yield

@pytest.fixture
def mock_weaviate_client():
    yield mock_weaviate_client.return_value


# Test for searching tenant uploaded files
def test_search_tenant_files(mock_auth, mock_weaviate_client):
    # Define test request data
    request_data = {
        "query": "financial reports 2023",
        "organization_id": "test-org",
        "tenant_id": "default",
        "filters": {},
        "limit": 5
    }
    
    # Make the request to the endpoint
    response = client.post("/api/v1/rag/tenant-files/search", json=request_data)
    
    # Assert response status code
    assert response.status_code == 200
    
    # Assert response content
    data = response.json()
    assert "files" in data
    assert len(data["files"]) == 2
    assert data["files"][0]["file_id"] == "test-file-id-1"
    assert data["files"][1]["file_id"] == "test-file-id-2"
    assert data["query"] == "financial reports 2023"
    
    # No need to verify mock calls since we're using a mock class
    # Just verify the response is correct


# Test for getting a tenant file by ID
def test_get_tenant_file_by_id(mock_auth, mock_weaviate_client):
    # Make the request to the endpoint
    response = client.get("/api/v1/rag/tenant-files/test-file-id-1?organization_id=test-org")
    
    # Assert response status code
    assert response.status_code == 200
    
    # Assert response content
    data = response.json()
    assert data["file_id"] == "test-file-id-1"
    assert data["file_name"] == "test_document.pdf"
    assert data["organization_id"] == "test-org"
    
    # Verify the mock was called with the correct arguments
    mock_weaviate_client.query_documents.assert_called_once_with(
        query="",
        filters={
            "tenant_id": "default",
            "organization_id": "test-org",
            "file_id": "test-file-id-1"
        },
        limit=1,
        class_name="Tenant_UploadedFiles"
    )


# Test for file not found
def test_get_tenant_file_not_found(mock_auth, mock_weaviate_client):
    # Mock empty result for non-existent file
    mock_weaviate_client.query_documents.return_value = []
    
    # Make the request to the endpoint
    response = client.get("/api/v1/rag/tenant-files/non-existent-id?organization_id=test-org")
    
    # Assert response status code
    assert response.status_code == 404
    
    # Assert error message
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


# Test for tenant file upload
@pytest.mark.asyncio
async def test_upload_tenant_file(mock_auth):
    # Get the mocked ingestion graph
    mock_graph = mock_ingestion_graph.return_value
    
    # Create a test file
    test_file_content = b"This is a test PDF file content"
    test_file_path = "test_upload.pdf"
    
    try:
        # Write test file
        with open(test_file_path, "wb") as f:
            f.write(test_file_content)
        
        # Make the request to the endpoint
        with open(test_file_path, "rb") as f:
            response = client.post(
                "/api/v1/rag/ingest/tenant-file",
                files={"file": ("test_upload.pdf", f, "application/pdf")},
                data={
                    "organization_id": "test-org",
                    "tenant_id": "default",
                    "file_tags": "financial,test,2023"
                }
            )
        
        # Assert response status code
        assert response.status_code == 200
        
        # Assert response content
        data = response.json()
        assert "job_id" in data
        
        # Verify the mock was called
        mock_graph.ingest_document_async.assert_called_once()
        
        # Check the arguments passed to ingest_document_async
        call_args = mock_graph.ingest_document_async.call_args[1]
        assert call_args["tenant_id"] == "default"
        assert "input_data" in call_args
        assert call_args["input_data"]["source_type"] == "tenant_uploaded_file"
        assert call_args["input_data"]["metadata"]["organization_id"] == "test-org"
        assert "financial" in call_args["input_data"]["metadata"]["tags"]
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


# Test for tenant file upload without organization_id
def test_upload_tenant_file_without_org_id(mock_auth):
    # Make the request to the endpoint without organization_id
    with open(__file__, "rb") as f:  # Use this test file itself
        response = client.post(
            "/api/v1/rag/ingest/tenant-file",
            files={"file": ("test.py", f, "text/plain")},
            data={"tenant_id": "default"}
        )
    
    # Assert response status code
    assert response.status_code == 400
    
    # Assert error message
    data = response.json()
    assert "detail" in data
    assert "organization_id is required" in data["detail"]


# Cleanup function to restore original classes
def teardown_module(module):
    global TenantUploadedFilesSearchTool
    TenantUploadedFilesSearchTool = original_tool
    
    # Reset all mocks
    mock_tenant_files_tool.reset_mock()
    mock_current_user.reset_mock()
    mock_ingestion_graph.reset_mock()
    mock_weaviate_client.reset_mock()
    
    # Remove dependency overrides
    app.dependency_overrides = {}

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])