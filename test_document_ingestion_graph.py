import asyncio
from unittest.mock import MagicMock
from src.ingestion.graph import IngestionGraph
from langsmith import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

async def test_document_ingestion():
    # LangSmith configuration is already set in .env:
    # LANGSMITH_API_KEY
    # LANGSMITH_TRACING=true
    # LANGSMITH_PROJECT=synthdrive-rag-service

    # Create mock clients
    postgres_client = MagicMock()
    weaviate_client = MagicMock()
    neo4j_client = MagicMock()

    # Create ingestion graph with mock clients
    graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        use_graphrag=False
    )

    # Test payload
    input_data = {
        "content": "SynthDrive Inc. is working on a new AI project called Project Horizon...",
        "metadata": {
            "source": "company_report",
            "author": "John Smith",
            "created_at": "2025-10-25T09:00:00Z",
            "document_type": "internal_memo",
            "tags": ["AI", "project", "confidential"],
            "additional_metadata": {
                "priority": "high",
                "department": "R&D"
            }
        }
    }

    # Run the ingestion graph
    try:
        # This will be traced in LangSmith under the project specified in .env
        result = await graph.ingest_document_async(
            input_data=input_data,
            tenant_id="default"
        )
        print("Graph nodes traversed successfully")
        print("Ingestion result:", result)
        
        # Print the destinations where the document was routed
        if "destinations" in result:
            print("Document was routed to:", result["destinations"])
        
        print("\nTo view the trace in LangSmith Studio:")
        print("1. Go to https://smith.langchain.com")
        print("2. Select the 'synthdrive-rag-service' project")
        print("3. You'll see the graph visualization showing:")
        print("   - load_document -> chunk_and_embed -> extract_entities -> route_to_stores")
        print("   - Conditional routing to storage nodes based on content type")
            
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_document_ingestion())