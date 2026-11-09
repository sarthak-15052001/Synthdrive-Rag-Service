from typing import Dict, Any
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.main import app
from src.api.v1.schemas import IngestRequest, QueryRequest, IngestResponse, Response, Citation

class DummyPostgresClient:
    def add_document(self, *args, **kwargs): pass
    def get_document_by_id(self, *args, **kwargs): return None
    def search_documents(self, *args, **kwargs): return []
    def delete_document(self, *args, **kwargs): return False
    def close(self): pass

class DummyWeaviateClient:
    def create_embedding(self, *args, **kwargs): return [0.0] * 1536
    def add_document(self, *args, **kwargs): return "dummy-id"
    def query_documents(self, *args, **kwargs): return []
    def close(self): pass

class DummyNeo4jClient:
    def add_document(self, *args, **kwargs): pass
    def get_document_by_id(self, *args, **kwargs): return None
    def get_related_documents(self, *args, **kwargs): return []
    def search_documents(self, *args, **kwargs): return []
    def close(self): pass

@pytest.fixture
def client():
    # Initialize app state with dummy clients
    app.state.postgres_client = DummyPostgresClient()
    app.state.weaviate_client = DummyWeaviateClient()
    app.state.neo4j_client = DummyNeo4jClient()
    app.state.neo4j_graphrag_client = None
    return TestClient(app)

@pytest.fixture
def mock_ingestion_graph():
    with patch("src.api.v1.endpoints.ingest.get_ingestion_graph") as mock:
        graph = MagicMock()
        async def mock_ingest(*args, **kwargs):
            return {"status": "success"}
        graph.ingest_document_async = AsyncMock(side_effect=mock_ingest)
        mock.return_value = graph
        yield graph

@pytest.fixture
def mock_query_graph():
    with patch("src.api.v1.endpoints.query.get_query_graph") as mock:
        graph = MagicMock()
        def mock_query(*args, **kwargs):
            return {
                "answer": "Test answer",
                "sources": [
                    {
                        "id": "doc1",
                        "source": "test",
                        "content": "test content",
                        "metadata": {"author": "tester"}
                    }
                ],
                "reasoning": "Test reasoning",
                "synthesis": "Test synthesis"
            }
        graph.query = mock_query
        mock.return_value = graph
        yield graph

@pytest.fixture
def mock_current_user():
    with patch("src.api.v1.endpoints.ingest.get_current_user") as mock_ingest, \
         patch("src.api.v1.endpoints.query.get_current_user") as mock_query:
        user_data = {"id": "test-user"}
        mock_ingest.return_value = user_data
        mock_query.return_value = user_data
        yield

@pytest.mark.asyncio
async def test_ingest_endpoint(client, mock_ingestion_graph, mock_current_user):
    """Test the /ingest endpoint"""
    request_data = {
        "content": "Test content",
        "tenant_id": "test-tenant",
        "metadata": {
            "source": "test",
            "author": "tester"
        }
    }
    
    response = client.post("/api/v1/rag/ingest", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)

@pytest.mark.asyncio
async def test_ingest_endpoint_error(client, mock_ingestion_graph, mock_current_user):
    """Test error handling in /ingest endpoint"""
    # Configure mock to raise an exception
    async def mock_error(*args, **kwargs):
        raise RuntimeError("Test error")
    mock_ingestion_graph.ingest_document_async = AsyncMock(side_effect=mock_error)
    
    response = client.post("/api/v1/rag/ingest",
        json={"content": "test", "tenant_id": "test-tenant"})
    
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_query_endpoint(client, mock_query_graph, mock_current_user):
    """Test the /query endpoint streaming response"""
    
    request_data = {
        "query_str": "test query",
        "tenant_id": "test-tenant",
        "top_k": 5
    }
    
    with client.stream("POST", "/api/v1/rag/query", json=request_data) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Collect all chunks
        chunks = []
        for chunk in response.iter_lines():
            if chunk:
                if isinstance(chunk, bytes):
                    chunk = chunk.decode()
                if chunk.startswith("data: "):
                    chunks.append(json.loads(chunk.replace("data: ", "")))
        
        # Verify all parts received
        assert any("answer" in chunk for chunk in chunks)
        assert any("citations" in chunk for chunk in chunks)
        assert any("reasoning" in chunk for chunk in chunks)
        assert any("synthesis" in chunk for chunk in chunks)
        
        # Verify content
        answer_chunk = next(c for c in chunks if "answer" in c)
        assert answer_chunk["answer"] == "Test answer"
        
        citations_chunk = next(c for c in chunks if "citations" in c)
        assert len(citations_chunk["citations"]) == 1
        assert citations_chunk["citations"][0]["id"] == "doc1"

@pytest.mark.asyncio
async def test_query_endpoint_error(client, mock_query_graph, mock_current_user):
    """Test error handling in /query endpoint"""
    # Configure mock to raise an exception
    def mock_error(*args, **kwargs):
        raise RuntimeError("Test error")
    mock_query_graph.query = mock_error
    
    request_data = {
        "query_str": "test query",
        "tenant_id": "test-tenant"
    }
    
    with client.stream("POST", "/api/v1/rag/query", json=request_data) as response:
        assert response.status_code == 200
        
        # Should get error message in stream
        chunks = []
        for chunk in response.iter_lines():
            if chunk:
                if isinstance(chunk, bytes):
                    chunk = chunk.decode()
                if chunk.startswith("data: "):
                    chunks.append(json.loads(chunk.replace("data: ", "")))
        
        assert len(chunks) == 1
        assert "error" in chunks[0]
        assert "test error" in chunks[0]["error"].lower()