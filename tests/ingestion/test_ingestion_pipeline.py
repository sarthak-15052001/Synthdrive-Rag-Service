import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
import json

from src.ingestion.graph import IngestionGraph, IngestionState
from src.ingestion.nodes import (
    load_document,
    chunk_and_embed,
    extract_entities,
    route_to_stores,
    store_in_weaviate,
    store_in_neo4j
)
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient


# Mock clients for testing
@pytest.fixture
def mock_postgres_client():
    client = MagicMock(spec=PostgresClient)
    client.add_document.return_value = None
    return client


@pytest.fixture
def mock_weaviate_client():
    client = MagicMock(spec=WeaviateClient)
    client.add_document.return_value = None
    return client


@pytest.fixture
def mock_neo4j_client():
    client = MagicMock(spec=Neo4jClient)
    client.add_document.return_value = None
    client.add_entity.return_value = None
    client.add_relationship.return_value = None
    return client


@pytest.fixture
def ingestion_graph(mock_postgres_client, mock_weaviate_client, mock_neo4j_client):
    return IngestionGraph(mock_postgres_client, mock_weaviate_client, mock_neo4j_client)


@pytest.fixture
def sample_text_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("This is a sample document for testing. It mentions John Doe who works at Acme Corp in New York.")
        file_path = f.name
    
    yield file_path
    
    # Clean up
    os.unlink(file_path)


class TestIngestionNodes:
    """Test individual ingestion nodes."""
    
    def test_load_document_with_file(self, sample_text_file):
        """Test loading a document from a file."""
        input_data = {
            "file_path": sample_text_file,
            "metadata": {"source": "test"}
        }
        tenant_id = "test_tenant"
        
        result = load_document(input_data, tenant_id)
        
        assert "input_data" in result
        assert "content" in result["input_data"]
        assert "metadata" in result["input_data"]
        assert result["input_data"]["metadata"]["tenant_id"] == tenant_id
        assert "document_id" in result["input_data"]["metadata"]
    
    def test_load_document_with_content(self):
        """Test loading a document from direct content."""
        content = "This is a test document."
        input_data = {
            "content": content,
            "metadata": {"source": "direct_input"}
        }
        tenant_id = "test_tenant"
        
        result = load_document(input_data, tenant_id)
        
        assert "input_data" in result
        assert result["input_data"]["content"] == content
        assert result["input_data"]["metadata"]["tenant_id"] == tenant_id
    
    @patch("src.ingestion.nodes.OpenAIEmbeddings")
    def test_chunk_and_embed(self, mock_embeddings):
        """Test chunking and embedding a document."""
        # Mock the embeddings model
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_embeddings.return_value = mock_embeddings_instance
        
        input_data = {
            "content": "This is a test document that should be chunked and embedded.",
            "metadata": {"source": "test"}
        }
        tenant_id = "test_tenant"
        
        result = chunk_and_embed(input_data, tenant_id)
        
        assert "processed_chunks" in result
        assert "embeddings" in result
        assert len(result["processed_chunks"]) > 0
        assert len(result["embeddings"]) > 0
        assert result["processed_chunks"][0]["metadata"]["tenant_id"] == tenant_id
    
    @patch("src.ingestion.nodes.OpenAI")
    def test_extract_entities(self, mock_openai):
        """Test extracting entities from document chunks."""
        # Mock the OpenAI client
        mock_openai_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Set up the mock response
        mock_message.content = json.dumps({
            "entities": [
                {"name": "John Doe", "type": "PERSON", "id": "1"},
                {"name": "Acme Corp", "type": "ORGANIZATION", "id": "2"}
            ],
            "relationships": [
                {"source_id": "1", "target_id": "2", "type": "WORKS_AT", "description": "John Doe works at Acme Corp"}
            ]
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        processed_chunks = [
            {
                "content": "John Doe works at Acme Corp.",
                "metadata": {"chunk_id": 0, "document_id": "123", "tenant_id": "test_tenant"}
            }
        ]
        tenant_id = "test_tenant"
        
        result = extract_entities(processed_chunks, tenant_id)
        
        assert "entities" in result
        assert "entities" in result["entities"]
        assert "relationships" in result["entities"]
        assert len(result["entities"]["entities"]) > 0
        assert len(result["entities"]["relationships"]) > 0
    
    def test_route_to_stores(self):
        """Test routing to data stores."""
        processed_chunks = [{"content": "Test", "metadata": {}}]
        embeddings = [[0.1, 0.2, 0.3]]
        entities = {
            "entities": [{"name": "John Doe", "type": "PERSON", "id": "1"}],
            "relationships": []
        }
        tenant_id = "test_tenant"
        
        result = route_to_stores(processed_chunks, embeddings, entities, tenant_id)
        
        assert "destinations" in result
        assert "weaviate" in result["destinations"]
        assert "neo4j" in result["destinations"]
        
        # Test with no entities
        result_no_entities = route_to_stores(processed_chunks, embeddings, {"entities": [], "relationships": []}, tenant_id)
        assert "weaviate" in result_no_entities["destinations"]
        assert "neo4j" not in result_no_entities["destinations"]


class TestIngestionGraph:
    """Test the ingestion graph as a whole."""
    
    @patch("src.ingestion.nodes.OpenAIEmbeddings")
    @patch("src.ingestion.nodes.OpenAI")
    async def test_ingest_document_async(self, mock_openai, mock_embeddings, ingestion_graph):
        """Test the async document ingestion flow."""
        # Mock the embeddings model
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock the OpenAI client
        mock_openai_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Set up the mock response
        mock_message.content = json.dumps({
            "entities": [
                {"name": "John Doe", "type": "PERSON", "id": "1"},
                {"name": "Acme Corp", "type": "ORGANIZATION", "id": "2"}
            ],
            "relationships": [
                {"source_id": "1", "target_id": "2", "type": "WORKS_AT", "description": "John Doe works at Acme Corp"}
            ]
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        # Test data
        input_data = {
            "content": "This is a test document. It mentions John Doe who works at Acme Corp.",
            "metadata": {"source": "test"}
        }
        tenant_id = "test_tenant"
        
        # Run the ingestion graph
        result = await ingestion_graph.ingest_document_async(input_data, tenant_id)
        
        # Verify the result
        assert result["status"] == "success"
        assert "destinations" in result
        
        # Verify that the store methods were called
        ingestion_graph.weaviate_client.add_document.assert_called()
        ingestion_graph.neo4j_client.add_document.assert_called()
        ingestion_graph.neo4j_client.add_entity.assert_called()
        ingestion_graph.neo4j_client.add_relationship.assert_called()
    
    @patch("src.ingestion.nodes.OpenAIEmbeddings")
    @patch("src.ingestion.nodes.OpenAI")
    def test_ingest_document_sync(self, mock_openai, mock_embeddings, ingestion_graph):
        """Test the synchronous document ingestion flow."""
        # Mock the embeddings model
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock the OpenAI client
        mock_openai_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Set up the mock response
        mock_message.content = json.dumps({
            "entities": [
                {"name": "John Doe", "type": "PERSON", "id": "1"},
                {"name": "Acme Corp", "type": "ORGANIZATION", "id": "2"}
            ],
            "relationships": [
                {"source_id": "1", "target_id": "2", "type": "WORKS_AT", "description": "John Doe works at Acme Corp"}
            ]
        })
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance
        
        # Test data
        input_data = {
            "content": "This is a test document. It mentions John Doe who works at Acme Corp.",
            "metadata": {"source": "test"}
        }
        tenant_id = "test_tenant"
        
        # Run the ingestion graph
        result = ingestion_graph.ingest_document(input_data, tenant_id)
        
        # Verify the result
        assert result["status"] == "success"
        assert "destinations" in result
        
        # Verify that the store methods were called
        ingestion_graph.weaviate_client.add_document.assert_called()
        ingestion_graph.neo4j_client.add_document.assert_called()
        ingestion_graph.neo4j_client.add_entity.assert_called()
        ingestion_graph.neo4j_client.add_relationship.assert_called()


if __name__ == "__main__":
    pytest.main()