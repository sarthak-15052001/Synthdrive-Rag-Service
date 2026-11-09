import asyncio
import logging
from typing import Dict, List, Any

from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.global_knowledge_domain import GlobalKnowledgeDomain
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

async def test_global_knowledge_domain():
    """Test the Global Knowledge Domain for AI tools search."""
    
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
        
        # Initialize Global Knowledge Domain
        global_knowledge_domain = GlobalKnowledgeDomain(weaviate_client=weaviate_client)
        
        # Test queries
        test_queries = [
            "tool for video from text",
            "I need something to help with coding",
            "tool for data visualization",
            "AI for content creation"
        ]
        
        # Run test queries
        logger.info("Testing Global Knowledge Domain with sample queries")
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Search for AI tools using Global Knowledge Domain
            result = await global_knowledge_domain.search_ai_tools(
                query=query,
                limit=3,
                explain=True
            )
            
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
                
                # Display explanation if available
                explanation = result.get("explanations", {}).get(tool.get("name", ""), "")
                if explanation:
                    logger.info(f"  Explanation: {explanation}")
                
                logger.info("---")
        
        # Clean up
        logger.info("Test completed")
        weaviate_client.close()
        return True
    
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_global_knowledge_domain())