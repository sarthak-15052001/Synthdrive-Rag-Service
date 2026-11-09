import asyncio
import logging
from typing import Dict, List, Any

from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.vector_search import VectorSearchTool
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_search_ai_tools():
    """Test searching for AI tools using the VectorSearchTool."""
    try:
        # Initialize Weaviate client
        weaviate_url = settings.WEAVIATE_URL
        weaviate_api_key = settings.WEAVIATE_API_KEY
        
        logger.info(f"Connecting to Weaviate at {weaviate_url}")
        weaviate_client = WeaviateClient(weaviate_url=weaviate_url, api_key=weaviate_api_key)
        
        # Initialize vector search tool
        vector_search_tool = VectorSearchTool(weaviate_client=weaviate_client)
        
        # Test queries
        test_queries = [
            "find a tool to make videos from text",
            "I need something to help with coding",
            "tool for data visualization",
            "AI for content creation",
            "translation tool"
        ]
        
        # Run test queries
        logger.info("Testing AI tool search with real data")
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Search for AI tools
            results = await vector_search_tool.search_ai_tools(query=query, limit=3)
            
            # Display results
            logger.info(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Name: {result.get('name')}")
                logger.info(f"  Description: {result.get('description')}")
                logger.info(f"  Use Case: {result.get('use_case', '')}")
                logger.info(f"  URL: {result.get('url')}")
                logger.info(f"  Category: {result.get('category', '')}")
                logger.info(f"  Pricing: {result.get('pricing', '')}")
                logger.info(f"  Rating: {result.get('rating', '')}")
                logger.info(f"  Relevance Score: {result.get('relevance_score')}")
                logger.info("---")
        
        logger.info("\nTest completed successfully")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        # Close the client
        if 'weaviate_client' in locals():
            weaviate_client.close()

if __name__ == "__main__":
    asyncio.run(test_search_ai_tools())