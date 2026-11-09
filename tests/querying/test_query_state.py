import pytest
from src.querying.graph import QueryGraph, QueryState
from unittest.mock import MagicMock

def test_query_state_flow():
    # Mock clients
    postgres_client = MagicMock()
    weaviate_client = MagicMock()
    neo4j_client = MagicMock()
    
    # Mock vector search results
    weaviate_client.query_documents.return_value = [
        {
            "content": "Test document content",
            "source": "test.pdf",
            "metadata": {"page": 1}
        }
    ]
    
    # Create graph
    graph = QueryGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        use_graphrag=False
    )
    
    # Test query
    result = graph.query(
        query="What is the test about?",
        filters={"tenant_id": "test"},
        top_k=1
    )
    
    # Verify result structure
    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    assert "reasoning" in result
    assert "synthesis" in result
    
    # Verify weaviate was called
    weaviate_client.query_documents.assert_called_once()