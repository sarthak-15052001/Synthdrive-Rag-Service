import pytest
from unittest.mock import MagicMock, patch
from src.querying.tools.vector_search import VectorSearchTool
from src.querying.tools.graph_retrieval import GraphRetrievalTool

@pytest.fixture
def mock_weaviate_client():
    client = MagicMock()
    client.query_documents.return_value = [
        {
            "content": "Test document content",
            "metadata": {"page": 1},
            "source": "test.pdf",
            "relevance_score": 0.95
        }
    ]
    return client

@pytest.fixture
def mock_neo4j_client():
    client = MagicMock()
    client.traverse_relations.return_value = [
        {
            "document_id": "doc1",
            "content": "Test graph content",
            "metadata": {"type": "document"},
            "source": "graph.pdf"
        }
    ]
    client.get_document_by_id.return_value = {
        "content": "Full document content",
        "metadata": {"type": "document"},
        "source": "graph.pdf"
    }
    return client

@pytest.mark.asyncio
async def test_vector_search(mock_weaviate_client):
    tool = VectorSearchTool(mock_weaviate_client)
    results = await tool.search("test query", {"tenant_id": "test"}, 5)
    
    assert len(results) > 0
    assert "content" in results[0]
    assert "citation_id" in results[0]
    assert results[0]["citation_id"].startswith("vector-")
    mock_weaviate_client.query_documents.assert_called_once()

@pytest.mark.asyncio
async def test_hybrid_search(mock_weaviate_client):
    tool = VectorSearchTool(mock_weaviate_client)
    results = await tool.hybrid_search("test query", {"tenant_id": "test"}, 5)
    
    assert len(results) > 0
    assert "content" in results[0]
    assert "citation_id" in results[0]
    assert results[0]["citation_id"].startswith("hybrid-")

@pytest.mark.asyncio
async def test_graph_traversal(mock_neo4j_client):
    tool = GraphRetrievalTool(mock_neo4j_client)
    results = await tool.traverse_relations("test query", "test_tenant", 5)
    
    assert len(results) > 0
    assert "content" in results[0]
    assert "citation_id" in results[0]
    assert "graph_context" in results[0]
    mock_neo4j_client.traverse_relations.assert_called_once()

@pytest.mark.asyncio
async def test_cypher_generation(mock_neo4j_client):
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="MATCH (n:Document) RETURN n LIMIT 5"))
        ]
        
        tool = GraphRetrievalTool(mock_neo4j_client)
        cypher = await tool.generate_cypher("Find all documents")
        
        assert cypher.strip().startswith("MATCH")
        assert "Document" in cypher

@pytest.mark.asyncio
async def test_find_related_entities(mock_neo4j_client):
    tool = GraphRetrievalTool(mock_neo4j_client)
    results = await tool.find_related_entities("TestEntity", "test_tenant", 2, 5)
    
    assert len(results) > 0
    mock_neo4j_client.traverse_relations.assert_called_once()

@pytest.mark.asyncio
async def test_find_paths_between_entities(mock_neo4j_client):
    tool = GraphRetrievalTool(mock_neo4j_client)
    results = await tool.find_paths_between_entities("EntityA", "EntityB", "test_tenant", 3)
    
    assert len(results) > 0
    mock_neo4j_client.traverse_relations.assert_called_once()