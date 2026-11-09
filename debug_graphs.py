"""Debug and visualize LangGraph flows in LangSmith."""
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from langchain_core.runnables import RunnableConfig

from src.ingestion.ingestion_pipelines import create_document_ingestion_graph

async def test_document_ingestion():
    """Test and visualize document ingestion flow."""
    # Create config for LangSmith tracing
    config = RunnableConfig(
        tags=["test", "document_ingestion"],
        metadata={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "document_ingestion"
        }
    )
    
    # Create the graph using existing pipeline
    graph = create_document_ingestion_graph(config)
    
    # Sample payload matching the API request
    job_id = str(uuid4())
    initial_state = {
        "input_data": {
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
            },
            "job_id": job_id,
            "source_type": "document"
        },
        "tenant_id": "default",
        "processed_chunks": None,
        "embeddings": None,
        "entities": None,
        "destinations": None,
        "error": None
    }
    
    # Invoke the graph
    try:
        result = await graph.ainvoke(initial_state, config)
        print(f"Graph execution completed. Result: {result}")
    except Exception as e:
        print(f"Error executing graph: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_document_ingestion())