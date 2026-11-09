import os
import pytest
import asyncio
from pathlib import Path

from src.ingestion.graph import IngestionGraph
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.core.config import settings


@pytest.fixture
def postgres_client():
    """Create a PostgreSQL client for testing."""
    client = PostgresClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        db=settings.POSTGRES_DB
    )
    return client


@pytest.fixture
def weaviate_client():
    """Create a Weaviate client for testing."""
    client = WeaviateClient(
        url=settings.WEAVIATE_URL,
        api_key=settings.WEAVIATE_API_KEY
    )
    return client


@pytest.fixture
def neo4j_client():
    """Create a Neo4j client for testing."""
    client = Neo4jClient(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    return client


@pytest.fixture
def ingestion_graph(postgres_client, weaviate_client, neo4j_client):
    """Create an ingestion graph for testing."""
    return IngestionGraph(postgres_client, weaviate_client, neo4j_client)


@pytest.fixture
def test_data_path():
    """Get the path to the test data file."""
    current_dir = Path(__file__).parent
    return os.path.join(current_dir, "test_data.txt")


class TestIngestionIntegration:
    """Integration tests for the ingestion pipeline."""
    
    @pytest.mark.asyncio
    async def test_ingest_file(self, ingestion_graph, test_data_path):
        """Test ingesting a file through the pipeline."""
        # Test data
        input_data = {
            "file_path": test_data_path,
            "metadata": {
                "source": "integration_test",
                "document_type": "text",
                "tags": ["test", "integration"]
            }
        }
        tenant_id = "test_tenant_integration"
        
        # Run the ingestion graph
        result = await ingestion_graph.ingest_document_async(input_data, tenant_id)
        
        # Verify the result
        assert result["status"] == "success"
        assert "destinations" in result
        assert len(result["destinations"]) > 0
        
        # Verify data was stored in Weaviate
        if "weaviate" in result["destinations"]:
            # Query Weaviate to verify the document was stored
            weaviate_client = ingestion_graph.weaviate_client
            query_result = weaviate_client.query_documents(
                query="Acme Corporation",
                filters={"tenant_id": tenant_id},
                limit=5
            )
            
            # Verify the query result
            assert len(query_result) > 0
            assert any("Acme Corporation" in doc["content"] for doc in query_result)
        
        # Verify data was stored in Neo4j
        if "neo4j" in result["destinations"]:
            # Query Neo4j to verify the entities were stored
            neo4j_client = ingestion_graph.neo4j_client
            query_result = neo4j_client.query_entities(
                query="MATCH (e:Entity) WHERE e.tenant_id = $tenant_id RETURN e",
                params={"tenant_id": tenant_id}
            )
            
            # Verify the query result
            assert len(query_result) > 0
            entity_names = [entity.get("name") for entity in query_result]
            assert any(name in ["John Smith", "Acme Corporation", "New York City"] for name in entity_names)
    
    @pytest.mark.asyncio
    async def test_ingest_content(self, ingestion_graph):
        """Test ingesting content directly through the pipeline."""
        # Test data
        content = """
        This is a direct content test for the ingestion pipeline.
        It mentions Sarah Johnson who is the CTO of TechInnovate Inc. based in Seattle.
        """
        
        input_data = {
            "content": content,
            "metadata": {
                "source": "direct_input",
                "document_type": "text",
                "tags": ["test", "integration", "direct"]
            }
        }
        tenant_id = "test_tenant_direct"
        
        # Run the ingestion graph
        result = await ingestion_graph.ingest_document_async(input_data, tenant_id)
        
        # Verify the result
        assert result["status"] == "success"
        assert "destinations" in result
        assert len(result["destinations"]) > 0
        
        # Verify data was stored in Weaviate
        if "weaviate" in result["destinations"]:
            # Query Weaviate to verify the document was stored
            weaviate_client = ingestion_graph.weaviate_client
            query_result = weaviate_client.query_documents(
                query="Sarah Johnson",
                filters={"tenant_id": tenant_id},
                limit=5
            )
            
            # Verify the query result
            assert len(query_result) > 0
            assert any("Sarah Johnson" in doc["content"] for doc in query_result)
    
    @pytest.mark.asyncio
    async def test_multi_tenancy(self, ingestion_graph, test_data_path):
        """Test multi-tenancy isolation in the ingestion pipeline."""
        # Test data for tenant 1
        input_data_1 = {
            "file_path": test_data_path,
            "metadata": {"source": "tenant1_test"}
        }
        tenant_id_1 = "test_tenant_1"
        
        # Test data for tenant 2
        content_2 = "This is a test document for tenant 2. It mentions different entities."
        input_data_2 = {
            "content": content_2,
            "metadata": {"source": "tenant2_test"}
        }
        tenant_id_2 = "test_tenant_2"
        
        # Run the ingestion graph for both tenants
        result_1 = await ingestion_graph.ingest_document_async(input_data_1, tenant_id_1)
        result_2 = await ingestion_graph.ingest_document_async(input_data_2, tenant_id_2)
        
        # Verify both results
        assert result_1["status"] == "success"
        assert result_2["status"] == "success"
        
        # Verify data isolation in Weaviate
        weaviate_client = ingestion_graph.weaviate_client
        
        # Query for tenant 1's data
        query_result_1 = weaviate_client.query_documents(
            query="Acme Corporation",
            filters={"tenant_id": tenant_id_1},
            limit=5
        )
        
        # Query for tenant 2's data
        query_result_2 = weaviate_client.query_documents(
            query="different entities",
            filters={"tenant_id": tenant_id_2},
            limit=5
        )
        
        # Verify tenant 1's data is only accessible with tenant 1's ID
        assert len(query_result_1) > 0
        assert any("Acme Corporation" in doc["content"] for doc in query_result_1)
        
        # Verify tenant 2's data is only accessible with tenant 2's ID
        assert len(query_result_2) > 0
        assert any("different entities" in doc["content"] for doc in query_result_2)
        
        # Cross-check: tenant 1's data should not be accessible with tenant 2's ID
        cross_check_1 = weaviate_client.query_documents(
            query="Acme Corporation",
            filters={"tenant_id": tenant_id_2},
            limit=5
        )
        assert len(cross_check_1) == 0
        
        # Cross-check: tenant 2's data should not be accessible with tenant 1's ID
        cross_check_2 = weaviate_client.query_documents(
            query="different entities",
            filters={"tenant_id": tenant_id_1},
            limit=5
        )
        assert len(cross_check_2) == 0


if __name__ == "__main__":
    pytest.main()