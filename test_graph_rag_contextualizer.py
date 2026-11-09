import asyncio
import json
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import necessary modules
from src.data_stores.neo4j_client import Neo4jClient
from src.querying.tools.graph_rag_contextualizer import GraphRAGContextualizer

async def test_graph_rag_contextualizer():
    """
    Test the Graph RAG Contextualizer with sample queries.
    """
    try:
        # Initialize Neo4j client
        neo4j_client = Neo4jClient()
        
        # Initialize the Graph RAG Contextualizer
        contextualizer = GraphRAGContextualizer(neo4j_client=neo4j_client)
        
        # Sample queries to test
        test_queries = [
            "Find workflows used by the Marketing team",
            "What are the relationships between the Sales and Engineering teams?",
            "Who created the Customer Onboarding workflow?",
            "Find potential knowledge silos in our organization",
            "What topics are discussed in multiple team meetings?"
        ]
        
        organization_id = "test_org"  # Replace with an actual organization ID if needed
        
        # Test each query
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            
            # Create a test state
            state = {
                'original_query': query,
                'organization_id': organization_id,
                'plan': None,
                'retrieved_docs': [],
                'graph_insights': [],
                'final_answer': None,
                'error_log': []
            }
            
            # Process the query with the Graph RAG Contextualizer
            result_state = await contextualizer.contextualize(state)
            
            # Check for errors
            if result_state.get('error_log'):
                logger.warning(f"Errors encountered: {result_state['error_log']}")
            
            # Log the number of insights found
            insights_count = len(result_state.get('graph_insights', []))
            logger.info(f"Found {insights_count} graph insights for query: {query}")
            
            # Print a sample of the insights (first 2)
            if insights_count > 0:
                logger.info("Sample insights:")
                for i, insight in enumerate(result_state.get('graph_insights', [])[:2]):
                    logger.info(f"Insight {i+1}:")
                    logger.info(f"  Content: {insight.get('content', 'N/A')}")
                    logger.info(f"  Explanation: {insight.get('explanation', 'N/A')[:100]}...")
                    logger.info(f"  Inferred Context: {insight.get('inferred_context', 'N/A')[:100]}...")
                    if 'business_implications' in insight:
                        logger.info(f"  Business Implications: {insight.get('business_implications', 'N/A')[:100]}...")
                    if 'knowledge_gaps' in insight:
                        logger.info(f"  Knowledge Gaps: {insight.get('knowledge_gaps', 'N/A')[:100]}...")
            
            logger.info("-" * 80)
        
        # Test multi-hop traversal specifically
        logger.info("Testing multi-hop traversal...")
        entity_name = "Marketing"  # Replace with an actual entity name if needed
        multi_hop_results = await contextualizer.find_multi_hop_paths(entity_name, organization_id)
        logger.info(f"Found {len(multi_hop_results)} multi-hop paths from entity '{entity_name}'")
        
        # Test knowledge silo discovery
        logger.info("Testing knowledge silo discovery...")
        silo_results = await contextualizer.discover_knowledge_silos(organization_id)
        logger.info(f"Found {len(silo_results)} potential knowledge silos")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error testing Graph RAG Contextualizer: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(test_graph_rag_contextualizer())