#!/usr/bin/env python3
"""
Example script demonstrating the ingestion pipeline functionality.

This script shows how to:
1. Initialize the ingestion graph
2. Ingest documents with different formats
3. Use multi-tenancy features
4. Handle async operations
"""

import asyncio
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
from src.ingestion.graph import IngestionGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_text_content_ingestion():
    """Example: Ingest text content directly (synchronous)"""
    logger.info("=" * 50)
    logger.info("Example 1: Text Content Ingestion (Sync)")
    logger.info("=" * 50)
    
    # Initialize clients (PostgreSQL is optional, not used in ingestion)
    try:
        postgres_client = PostgresClient()
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL not available (not required for ingestion): {e}")
        postgres_client = None
    
    weaviate_client = WeaviateClient()
    neo4j_client = Neo4jClient()
    
    # Create ingestion graph (postgres_client can be None)
    graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        use_graphrag=False
    )
    
    # Sample document content
    content = """
    Artificial Intelligence (AI) is transforming the technology industry. 
    Companies like OpenAI, Google, and Microsoft are leading the AI revolution.
    OpenAI's GPT-4 model has demonstrated remarkable capabilities in natural language understanding.
    Microsoft has integrated AI into their Azure cloud platform, making it accessible to enterprises worldwide.
    The partnership between Microsoft and OpenAI has accelerated AI adoption significantly.
    """
    
    # Prepare input data
    input_data = {
        "content": content,
        "metadata": {
            "source": "example_script",
            "title": "AI Industry Overview",
            "author": "System"
        }
    }
    
    # Ingest the document
    try:
        result = graph.ingest_document(
            input_data=input_data,
            tenant_id="company_123"
        )
        
        logger.info(f"✅ Ingestion successful!")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Message: {result['message']}")
        logger.info(f"   Destinations: {result['destinations']}")
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {str(e)}")
    
    # Cleanup
    weaviate_client.close()
    neo4j_client.close()
    if postgres_client:
        postgres_client.close()


async def example_async_ingestion():
    """Example: Async ingestion with GraphRAG support"""
    logger.info("=" * 50)
    logger.info("Example 2: Async Ingestion with GraphRAG")
    logger.info("=" * 50)
    
    # Initialize clients (PostgreSQL is optional)
    try:
        postgres_client = PostgresClient()
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL not available (not required for ingestion): {e}")
        postgres_client = None
    
    weaviate_client = WeaviateClient()
    neo4j_client = Neo4jClient()
    
    # Try to initialize GraphRAG client
    try:
        neo4j_graphrag_client = Neo4jGraphRAGClient()
        use_graphrag = True
        logger.info("📊 GraphRAG client initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ GraphRAG client unavailable: {str(e)}")
        neo4j_graphrag_client = None
        use_graphrag = False
    
    # Create ingestion graph with GraphRAG support
    graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        neo4j_graphrag_client=neo4j_graphrag_client,
        use_graphrag=use_graphrag
    )
    
    # Sample business document
    content = """
    Acme Corporation announced a strategic partnership with TechVentures Inc. on January 15, 2024.
    The partnership, valued at $50 million, will focus on developing next-generation cloud infrastructure.
    
    John Smith, CEO of Acme Corporation, stated: "This partnership represents a significant milestone 
    in our journey to become a leading cloud service provider."
    
    Sarah Johnson, CTO of TechVentures, emphasized the technical synergies: "Our combined expertise 
    in distributed systems and AI will enable us to deliver innovative solutions to enterprise customers."
    
    The joint venture will be headquartered in San Francisco, California, with additional offices 
    in New York and London. Operations are expected to commence in Q2 2024.
    """
    
    # Prepare input data
    input_data = {
        "content": content,
        "metadata": {
            "source": "press_release",
            "date": "2024-01-15",
            "category": "business_partnership",
            "importance": "high"
        }
    }
    
    # Async ingestion
    try:
        result = await graph.ingest_document_async(
            input_data=input_data,
            tenant_id="enterprise_456"
        )
        
        logger.info(f"✅ Async ingestion successful!")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Message: {result['message']}")
        logger.info(f"   Destinations: {result['destinations']}")
        logger.info(f"   GraphRAG: {'Enabled' if use_graphrag else 'Disabled'}")
        
    except Exception as e:
        logger.error(f"❌ Async ingestion failed: {str(e)}")
    
    # Cleanup
    weaviate_client.close()
    neo4j_client.close()
    if postgres_client:
        postgres_client.close()


async def example_multi_tenant_ingestion():
    """Example: Multi-tenant ingestion with data isolation"""
    logger.info("=" * 50)
    logger.info("Example 3: Multi-Tenant Data Isolation")
    logger.info("=" * 50)
    
    # Initialize clients (PostgreSQL is optional)
    try:
        postgres_client = PostgresClient()
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL not available (not required for ingestion): {e}")
        postgres_client = None
    
    weaviate_client = WeaviateClient()
    neo4j_client = Neo4jClient()
    
    # Create ingestion graph
    graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        use_graphrag=False
    )
    
    # Simulate documents from different tenants
    tenants_data = [
        {
            "tenant_id": "tenant_a",
            "content": "Company A's confidential product roadmap for 2024...",
            "metadata": {"classification": "confidential", "company": "Company A"}
        },
        {
            "tenant_id": "tenant_b", 
            "content": "Company B's public quarterly earnings report...",
            "metadata": {"classification": "public", "company": "Company B"}
        },
        {
            "tenant_id": "tenant_c",
            "content": "Company C's internal HR policies and procedures...",
            "metadata": {"classification": "internal", "company": "Company C"}
        }
    ]
    
    # Ingest documents for each tenant
    results = []
    for data in tenants_data:
        input_data = {
            "content": data["content"],
            "metadata": data["metadata"]
        }
        
        try:
            result = await graph.ingest_document_async(
                input_data=input_data,
                tenant_id=data["tenant_id"]
            )
            results.append({
                "tenant": data["tenant_id"],
                "status": result["status"],
                "destinations": result["destinations"]
            })
            logger.info(f"✅ Ingested document for {data['tenant_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest for {data['tenant_id']}: {str(e)}")
    
    # Summary
    logger.info("\n📊 Multi-Tenant Ingestion Summary:")
    for result in results:
        logger.info(f"   {result['tenant']}: {result['status']} -> {result['destinations']}")
    
    logger.info("\n🔒 Data isolation ensures each tenant's data is separate and secure")
    
    # Cleanup
    weaviate_client.close()
    neo4j_client.close()
    if postgres_client:
        postgres_client.close()


async def example_file_ingestion():
    """Example: Ingest a file (if test file exists)"""
    logger.info("=" * 50)
    logger.info("Example 4: File Ingestion")
    logger.info("=" * 50)
    
    # Check if test file exists
    test_file = Path(__file__).parent.parent / "tests" / "ingestion" / "test_data.txt"
    
    if not test_file.exists():
        logger.warning(f"⚠️ Test file not found: {test_file}")
        logger.info("Creating a sample file for demonstration...")
        
        # Create sample file
        test_file.parent.mkdir(parents=True, exist_ok=True)
        with open(test_file, "w") as f:
            f.write("""
Sample Document for Ingestion Testing

This is a test document containing information about various topics.
It includes references to people like Albert Einstein and Marie Curie,
organizations such as NASA and the European Space Agency,
and locations including New York City and the International Space Station.

The document discusses scientific achievements and technological advancements
in the fields of physics, chemistry, and space exploration.
""")
        logger.info(f"✅ Created test file: {test_file}")
    
    # Initialize clients (PostgreSQL is optional)
    try:
        postgres_client = PostgresClient()
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL not available (not required for ingestion): {e}")
        postgres_client = None
    
    weaviate_client = WeaviateClient()
    neo4j_client = Neo4jClient()
    
    # Create ingestion graph
    graph = IngestionGraph(
        postgres_client=postgres_client,
        weaviate_client=weaviate_client,
        neo4j_client=neo4j_client,
        use_graphrag=False
    )
    
    # Prepare input data with file path
    input_data = {
        "file_path": str(test_file),
        "metadata": {
            "source": "file_system",
            "file_type": "text"
        }
    }
    
    # Ingest the file
    try:
        result = await graph.ingest_document_async(
            input_data=input_data,
            tenant_id="file_test_tenant"
        )
        
        logger.info(f"✅ File ingestion successful!")
        logger.info(f"   File: {test_file.name}")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Destinations: {result['destinations']}")
        
    except Exception as e:
        logger.error(f"❌ File ingestion failed: {str(e)}")
    
    # Cleanup
    weaviate_client.close()
    neo4j_client.close()
    if postgres_client:
        postgres_client.close()


def main():
    """Run all examples"""
    logger.info("🚀 Starting Ingestion Pipeline Examples")
    logger.info("=" * 50)
    
    try:
        # Example 1: Synchronous text ingestion
        example_text_content_ingestion()
        
        # Example 2: Async ingestion with GraphRAG
        asyncio.run(example_async_ingestion())
        
        # Example 3: Multi-tenant ingestion
        asyncio.run(example_multi_tenant_ingestion())
        
        # Example 4: File ingestion
        asyncio.run(example_file_ingestion())
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ All examples completed successfully!")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Examples interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Error running examples: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()