import pytest
from pydantic import ValidationError
from src.api.v1.schemas import (
    TenantRequest,
    IngestRequest,
    QueryRequest,
    Response,
    Citation,
    DocumentMetadata
)

def test_tenant_request():
    """Test TenantRequest model"""
    # Test default tenant_id
    request = TenantRequest()
    assert request.tenant_id == "default"
    
    # Test custom tenant_id
    request = TenantRequest(tenant_id="custom")
    assert request.tenant_id == "custom"

def test_ingest_request():
    """Test IngestRequest model"""
    # Test minimal request
    request = IngestRequest(content="test content")
    assert request.content == "test content"
    assert request.tenant_id == "default"
    assert request.metadata is None
    
    # Test full request
    metadata = DocumentMetadata(
        source="test",
        author="test author",
        created_at="2023-01-01T00:00:00Z",
        document_type="text",
        tags=["test", "document"]
    )
    request = IngestRequest(
        content="test content",
        tenant_id="custom",
        metadata=metadata
    )
    assert request.content == "test content"
    assert request.tenant_id == "custom"
    assert request.metadata == metadata
    assert request.metadata.source == "test"
    assert request.metadata.tags == ["test", "document"]

def test_query_request():
    """Test QueryRequest model"""
    # Test minimal request
    request = QueryRequest(query_str="test query")
    assert request.query_str == "test query"
    assert request.tenant_id == "default"
    assert request.filters == {}
    assert request.top_k == 5
    
    # Test full request
    request = QueryRequest(
        query_str="test query",
        tenant_id="custom",
        filters={"type": "document"},
        top_k=10
    )
    assert request.query_str == "test query"
    assert request.tenant_id == "custom"
    assert request.filters == {"type": "document"}
    assert request.top_k == 10
    
    # Test top_k validation
    with pytest.raises(ValidationError):
        QueryRequest(query_str="test", top_k=0)
    with pytest.raises(ValidationError):
        QueryRequest(query_str="test", top_k=101)

def test_citation():
    """Test Citation model"""
    citation = Citation(
        id="test-1",
        source="test doc",
        content="test content",
        metadata={"type": "document"},
        relevance_score=0.95
    )
    assert citation.id == "test-1"
    assert citation.source == "test doc"
    assert citation.content == "test content"
    assert citation.metadata == {"type": "document"}
    assert citation.relevance_score == 0.95

def test_response():
    """Test Response model"""
    # Test minimal response
    response = Response(answer="test answer")
    assert response.answer == "test answer"
    assert response.citations == []
    assert response.reasoning is None
    assert response.synthesis is None
    
    # Test full response
    citation = Citation(
        id="test-1",
        source="test doc",
        content="test content",
        metadata={"type": "document"},
        relevance_score=0.95
    )
    response = Response(
        answer="test answer",
        citations=[citation],
        reasoning="test reasoning",
        synthesis="test synthesis"
    )
    assert response.answer == "test answer"
    assert len(response.citations) == 1
    assert response.citations[0] == citation
    assert response.reasoning == "test reasoning"
    assert response.synthesis == "test synthesis"