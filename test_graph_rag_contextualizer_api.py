import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_graph_rag_contextualizer_api():
    """
    Test the Graph RAG Contextualizer API endpoint with sample queries.
    """
    try:
        # API endpoint URL
        api_url = "http://localhost:8000/api/v1/graph-rag-contextualizer"
        
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
            logger.info(f"Testing API with query: {query}")
            
            # Create the request payload
            payload = {
                "query": query,
                "organization_id": organization_id,
                "tenant_id": "default",
                "retrieved_docs": []  # No retrieved docs for this test
            }
            
            # Make the API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token"  # Replace with actual token if needed
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            
            # Check the response
            if response.status_code == 200:
                result = response.json()
                insights_count = len(result.get("graph_insights", []))
                logger.info(f"API returned {insights_count} graph insights for query: {query}")
                
                # Print a sample of the insights (first 2)
                if insights_count > 0:
                    logger.info("Sample insights from API:")
                    for i, insight in enumerate(result.get("graph_insights", [])[:2]):
                        logger.info(f"Insight {i+1}:")
                        logger.info(f"  Content: {insight.get('content', 'N/A')}")
                        logger.info(f"  Explanation: {insight.get('explanation', 'N/A')[:100]}...")
                        logger.info(f"  Inferred Context: {insight.get('inferred_context', 'N/A')[:100]}...")
            else:
                logger.error(f"API request failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
            
            logger.info("-" * 80)
        
        logger.info("All API tests completed!")
        
    except Exception as e:
        logger.error(f"Error testing Graph RAG Contextualizer API: {str(e)}")
        raise

if __name__ == "__main__":
    test_graph_rag_contextualizer_api()