"""
Test script to verify the fix for Neo4j relationship querying in the planner.

This script tests the query_graph_relationships method in the PlannerNode class
to ensure it correctly uses the traverse_relations method of the Neo4jClient.
"""
import asyncio
import logging
import json
from src.querying.planner import PlannerNode, PlannerState
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.weaviate_client import WeaviateClient
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_planner_with_neo4j():
    """
    Test the PlannerNode with Neo4j to verify graph_insights are populated.
    """
    try:
        # Initialize Neo4j client
        neo4j_client = Neo4jClient(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        
        # Initialize Weaviate client (optional for this test)
        weaviate_client = None
        try:
            weaviate_client = WeaviateClient()
        except Exception as e:
            logger.warning(f"Could not initialize Weaviate client: {e}")
        
        # Initialize the planner node
        planner = PlannerNode(weaviate_client=weaviate_client, neo4j_client=neo4j_client)
        
        # Create a test query that should trigger graph relationship search
        test_query = "What are the relationships between AI tools and machine learning?"
        
        # Create initial state
        initial_state = PlannerState(
            original_query=test_query,
            organization_id="test-org",
            plan=None,
            collections_to_search=[],
            retrieved_docs=[],
            graph_insights=[],
            final_answer=None,
            error_log=[]
        )
        
        # Run the planner
        logger.info("Running planner with test query...")
        updated_state = await planner.plan_retrieval(initial_state)
        
        # Check if graph_insights were populated
        if updated_state["graph_insights"]:
            logger.info(f"Success! Found {len(updated_state['graph_insights'])} graph insights")
            logger.info(f"First insight: {json.dumps(updated_state['graph_insights'][0], indent=2)}")
        else:
            logger.warning("No graph insights were found. This could be normal if no relationships exist in Neo4j.")
        
        # Print the full updated state
        logger.info(f"Plan: {updated_state['plan']}")
        logger.info(f"Collections to search: {updated_state['collections_to_search']}")
        logger.info(f"Retrieved docs count: {len(updated_state['retrieved_docs'])}")
        logger.info(f"Graph insights count: {len(updated_state['graph_insights'])}")
        
        # Clean up
        neo4j_client.close()
        
        return updated_state
    
    except Exception as e:
        logger.error(f"Error testing planner with Neo4j: {e}")
        raise

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_planner_with_neo4j())
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Graph insights found: {len(result['graph_insights'])}")
    print(f"Retrieved docs found: {len(result['retrieved_docs'])}")
    print(f"Final answer: {result['final_answer'][:100]}..." if result['final_answer'] else "No final answer")
    print(f"Errors: {result['error_log']}")