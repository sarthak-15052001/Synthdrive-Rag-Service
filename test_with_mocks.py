from unittest.mock import MagicMock
import asyncio
import json
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.ingestion.graph import IngestionGraph


async def test_with_mocks():
    """Test the ingestion pipeline with mock clients."""
    print("Testing ingestion pipeline with mock clients...")
    
    # Create mock clients
    postgres_client = MagicMock(spec=PostgresClient)
    weaviate_client = MagicMock(spec=WeaviateClient)
    neo4j_client = MagicMock(spec=Neo4jClient)
    
    # Configure mock behavior
    weaviate_client.add_document.return_value = None
    neo4j_client.add_document.return_value = None
    neo4j_client.add_entity.return_value = None
    neo4j_client.add_relationship.return_value = None
    
    # Create ingestion graph with mock clients
    ingestion_graph = IngestionGraph(postgres_client, weaviate_client, neo4j_client)
    
    # Test data
    input_data = {
        "content": "This is a test document about John Doe who works at Acme Corp in New York.",
        "metadata": {
            "source": "test",
            "document_type": "text",
            "tags": ["test", "mock"]
        }
    }
    tenant_id = "test_tenant"
    
    print(f"\nIngesting document with tenant_id: {tenant_id}")
    print(f"Content: {input_data['content']}")
    print(f"Metadata: {json.dumps(input_data['metadata'], indent=2)}")
    
    # Run the ingestion graph
    try:
        result = await ingestion_graph.ingest_document_async(input_data, tenant_id)
        print("\nIngestion Result:")
        print(json.dumps(result, indent=2))
        
        # Verify the mock calls
        print("\nVerifying mock calls:")
        print(f"Weaviate add_document called: {weaviate_client.add_document.called}")
        print(f"Neo4j add_document called: {neo4j_client.add_document.called}")
        print(f"Neo4j add_entity called: {neo4j_client.add_entity.called}")
        
        print("\nTest completed successfully!")
        return True
    except Exception as e:
        print(f"\nError during ingestion: {str(e)}")
        return False


async def test_file_ingestion_with_mocks():
    """Test file ingestion with mock clients."""
    print("Testing file ingestion with mock clients...")
    
    # Create mock clients
    postgres_client = MagicMock(spec=PostgresClient)
    weaviate_client = MagicMock(spec=WeaviateClient)
    neo4j_client = MagicMock(spec=Neo4jClient)
    
    # Create ingestion graph with mock clients
    ingestion_graph = IngestionGraph(postgres_client, weaviate_client, neo4j_client)
    
    # Test data - simulating a file path
    input_data = {
        "file_path": "tests/ingestion/test_data.txt",
        "metadata": {
            "source": "test_file",
            "document_type": "text",
            "tags": ["test", "file", "mock"]
        }
    }
    tenant_id = "test_tenant_file"
    
    print(f"\nIngesting file with tenant_id: {tenant_id}")
    print(f"File path: {input_data['file_path']}")
    print(f"Metadata: {json.dumps(input_data['metadata'], indent=2)}")
    
    # Run the ingestion graph
    try:
        result = await ingestion_graph.ingest_document_async(input_data, tenant_id)
        print("\nIngestion Result:")
        print(json.dumps(result, indent=2))
        
        print("\nTest completed successfully!")
        return True
    except Exception as e:
        print(f"\nError during file ingestion: {str(e)}")
        return False


async def run_all_tests():
    """Run all mock tests."""
    print("=== Running All Mock Tests ===\n")
    
    # Run content ingestion test
    print("=== Test 1: Content Ingestion ===")
    await test_with_mocks()
    
    print("\n=== Test 2: File Ingestion ===")
    await test_file_ingestion_with_mocks()
    
    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(run_all_tests())