import asyncio
import logging
import json
import requests
from typing import Dict, List, Any

from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.vector_search_tools import VectorSearchToolsNode
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample AI tool data for testing
sample_tools = [
    {
        "name": "VideoGen AI",
        "description": "An AI tool that generates videos from text descriptions.",
        "use_case": "Create marketing videos, explainer videos, and social media content from text prompts.",
        "reviews": "Users praise its high-quality output and ease of use.",
        "url": "https://videogen-ai.example.com",
        "pricing": "Free tier with 5 videos/month, Pro tier at $29/month",
        "category": "Video Creation",
        "tags": ["video", "marketing", "content creation"],
        "rating": 4.7,
        "last_updated": "2025-09-15T00:00:00Z",
        "tenant_id": "default",
        "tool_id": "tool-001"
    },
    {
        "name": "CodeAssist",
        "description": "AI-powered code completion and generation tool.",
        "use_case": "Accelerate software development by generating code snippets and providing intelligent code completion.",
        "reviews": "Developers find it helpful for boilerplate code and learning new languages.",
        "url": "https://codeassist.example.com",
        "pricing": "Free for open source projects, $15/month for individuals, $49/month for teams",
        "category": "Development",
        "tags": ["coding", "programming", "developer tools"],
        "rating": 4.5,
        "last_updated": "2025-10-01T00:00:00Z",
        "tenant_id": "default",
        "tool_id": "tool-002"
    },
    {
        "name": "DataViz Pro",
        "description": "AI-powered data visualization tool that transforms data into interactive charts and graphs.",
        "use_case": "Create beautiful data visualizations for reports, presentations, and dashboards.",
        "reviews": "Business analysts love the intuitive interface and export options.",
        "url": "https://dataviz-pro.example.com",
        "pricing": "Free tier with basic features, $19/month for Pro features",
        "category": "Data Analysis",
        "tags": ["data", "visualization", "business intelligence"],
        "rating": 4.3,
        "last_updated": "2025-08-20T00:00:00Z",
        "tenant_id": "default",
        "tool_id": "tool-003"
    }
]

async def test_vector_search_tools_node():
    """Test the Vector Search Tools node directly."""
    
    try:
        # Initialize Weaviate client
        weaviate_url = settings.WEAVIATE_URL
        weaviate_api_key = settings.WEAVIATE_API_KEY
        
        logger.info(f"Connecting to Weaviate at {weaviate_url}")
        weaviate_client = WeaviateClient(weaviate_url=weaviate_url, api_key=weaviate_api_key)
        
        # Add sample tools to Weaviate
        logger.info("Adding sample AI tools to Weaviate")
        for tool in sample_tools:
            # Create content for embedding by combining relevant fields
            content = f"{tool['name']} {tool['description']} {tool['use_case']} {tool['category']}"
            
            # Create embedding
            embedding = weaviate_client.create_embedding(content)
            
            # Add to Weaviate
            try:
                weaviate_client.add_document(
                    content=content,
                    metadata=tool,
                    embedding=embedding,
                    class_name="Global_Tools"
                )
                logger.info(f"Added tool: {tool['name']}")
            except Exception as e:
                logger.error(f"Error adding tool {tool['name']}: {str(e)}")
        
        # Initialize Vector Search Tools node
        vector_search_tools_node = VectorSearchToolsNode(weaviate_client=weaviate_client)
        
        # Test queries
        test_queries = [
            "find AI tools for video generation",
            "I need something to help with coding",
            "tool for data visualization",
            "AI for content creation"
        ]
        
        # Run test queries
        logger.info("Testing Vector Search Tools node with sample queries")
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Create initial state
            initial_state = {
                "original_query": query,
                "organization_id": "default",
                "plan": None,
                "retrieved_docs": [],
                "graph_insights": [],
                "final_answer": None,
                "error_log": []
            }
            
            # Search for AI tools using Vector Search Tools node
            result_state = await vector_search_tools_node.search_ai_tools(initial_state)
            
            # Display results
            logger.info(f"Found {len(result_state.get('retrieved_docs', []))} results:")
            for i, tool in enumerate(result_state.get("retrieved_docs", [])):
                logger.info(f"Result {i+1}:")
                logger.info(f"  Name: {tool.get('name')}")
                logger.info(f"  Description: {tool.get('description')}")
                logger.info(f"  Use Case: {tool.get('use_case')}")
                logger.info(f"  URL: {tool.get('url')}")
                logger.info(f"  Category: {tool.get('category')}")
                logger.info(f"  Pricing: {tool.get('pricing')}")
                logger.info(f"  Rating: {tool.get('rating')}")
                logger.info(f"  Relevance Score: {tool.get('relevance_score')}")
                logger.info(f"  Citation ID: {tool.get('citation_id')}")
                logger.info("---")
        
        # Clean up
        logger.info("Test completed")
        weaviate_client.close()
        return True
    
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

def test_vector_search_tools_api():
    """Test the Vector Search Tools API endpoint."""
    
    try:
        # API endpoint URL
        api_url = "http://localhost:8000/api/v1/rag/vector-search-tools"
        
        # Test queries
        test_queries = [
            "find AI tools for video generation",
            "I need something to help with coding",
            "tool for data visualization",
            "AI for content creation"
        ]
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json"
        }
        
        # Try to get API key if available
        try:
            if hasattr(settings, 'API_KEY') and settings.API_KEY:
                headers["Authorization"] = f"Bearer {settings.API_KEY}"
        except Exception:
            logger.warning("API_KEY not found in settings, proceeding without authentication")
        
        # Check if the API server is running
        try:
            # Make a simple request to check if the server is running
            requests.get("http://localhost:8000/docs", timeout=2)
        except requests.exceptions.ConnectionError:
            logger.warning("API server is not running. Skipping API test.")
            return False
        
        # Run test queries
        logger.info("Testing Vector Search Tools API with sample queries")
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Request payload
            payload = {
                "query": query,
                "organization_id": "default",
                "tenant_id": "default"
            }
            
            # Make the API request
            response = requests.post(api_url, headers=headers, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                
                # Display results
                logger.info(f"Found {len(result.get('tools', []))} results:")
                for i, tool in enumerate(result.get("tools", [])):
                    logger.info(f"Result {i+1}:")
                    logger.info(f"  Name: {tool.get('name')}")
                    logger.info(f"  Description: {tool.get('description')}")
                    logger.info(f"  Use Case: {tool.get('use_case')}")
                    logger.info(f"  URL: {tool.get('url')}")
                    logger.info(f"  Category: {tool.get('category')}")
                    logger.info(f"  Pricing: {tool.get('pricing')}")
                    logger.info(f"  Rating: {tool.get('rating')}")
                    logger.info(f"  Relevance Score: {tool.get('relevance_score')}")
                    logger.info(f"  Citation ID: {tool.get('citation_id')}")
                    logger.info("---")
            else:
                logger.error(f"API request failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
        
        logger.info("API test completed")
        return True
    
    except Exception as e:
        logger.error(f"Error in API test: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the Vector Search Tools node
    logger.info("Testing Vector Search Tools node...")
    asyncio.run(test_vector_search_tools_node())
    
    # Test the Vector Search Tools API
    logger.info("\nTesting Vector Search Tools API...")
    test_vector_search_tools_api()