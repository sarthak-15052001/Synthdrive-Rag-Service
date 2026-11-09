#!/usr/bin/env python3
"""
Example script demonstrating how to use the RAG querying system.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.postgres_client import PostgresClient
from src.querying.agent import QueryAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('query_example.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_query_async(query: str):
    """
    Run a query asynchronously.
    
    Args:
        query: The query string
    """
    try:
        # Initialize clients
        weaviate_client = WeaviateClient()
        neo4j_client = Neo4jClient()
        postgres_client = PostgresClient()
        
        # Create the query agent
        agent = QueryAgent(
            postgres_client=postgres_client,
            weaviate_client=weaviate_client,
            neo4j_client=neo4j_client
        )
        
        logger.info(f"Running query: {query}")
        
        # Query the system asynchronously
        result = await agent.query_async(
            query=query,
            filters={"tenant_id": "default"},
            top_k=5
        )
        
        # Print the results
        print("\n" + "="*80)
        print(f"QUERY: {query}")
        print("="*80)
        print(f"ANSWER:\n{result['answer']}")
        print("-"*80)
        print("SOURCES:")
        
        for i, source in enumerate(result["sources"]):
            print(f"[{i+1}] {source.get('source', 'unknown')}: {source.get('content', '')[:100]}...")
        
        print("="*80 + "\n")
        
        return result
    
    except Exception as e:
        logger.error(f"Error running query: {str(e)}")
        raise


def run_query(query: str):
    """
    Run a query synchronously.
    
    Args:
        query: The query string
    """
    return asyncio.run(run_query_async(query))


def main():
    """Main function to run example queries."""
    # Load environment variables
    load_dotenv()
    
    # Example queries
    queries = [
        "What is artificial intelligence?",
        "How are machine learning and deep learning related?",
        "Explain the difference between supervised and unsupervised learning.",
        "What fields are part of artificial intelligence?"
    ]
    
    # Run each query
    for query in queries:
        try:
            run_query(query)
        except Exception as e:
            logger.error(f"Failed to run query '{query}': {str(e)}")


if __name__ == "__main__":
    main()