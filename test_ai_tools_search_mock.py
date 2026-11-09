import asyncio
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock data for testing
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
        "last_updated": "2025-09-15",
        "tenant_id": "default",
        "tool_id": "tool-001",
        "relevance_score": 0.95
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
        "last_updated": "2025-10-01",
        "tenant_id": "default",
        "tool_id": "tool-002",
        "relevance_score": 0.92
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
        "last_updated": "2025-08-20",
        "tenant_id": "default",
        "tool_id": "tool-003",
        "relevance_score": 0.88
    },
    {
        "name": "ContentCraft",
        "description": "AI content generation platform for various types of content.",
        "use_case": "Generate blog posts, social media content, product descriptions, and more.",
        "reviews": "Content marketers appreciate the quality and customization options.",
        "url": "https://contentcraft.example.com",
        "pricing": "$25/month for basic, $49/month for premium features",
        "category": "Content Creation",
        "tags": ["content", "marketing", "writing"],
        "rating": 4.6,
        "last_updated": "2025-09-10",
        "tenant_id": "default",
        "tool_id": "tool-004",
        "relevance_score": 0.91
    },
    {
        "name": "AITranslate",
        "description": "Neural machine translation tool with support for 100+ languages.",
        "use_case": "Translate documents, websites, and conversations with high accuracy.",
        "reviews": "International businesses rely on it for accurate translations.",
        "url": "https://aitranslate.example.com",
        "pricing": "Pay-as-you-go at $0.01 per 100 words, enterprise plans available",
        "category": "Language",
        "tags": ["translation", "language", "international"],
        "rating": 4.8,
        "last_updated": "2025-10-05",
        "tenant_id": "default",
        "tool_id": "tool-005",
        "relevance_score": 0.85
    }
]

# Mock search function
async def mock_search_ai_tools(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Mock function to simulate searching for AI tools.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        List of matching AI tools
    """
    logger.info(f"Mock searching for AI tools with query: {query}")
    
    # Simple keyword matching for demonstration
    query_terms = query.lower().split()
    results = []
    
    for tool in sample_tools:
        # Calculate a simple relevance score based on keyword matches
        score = 0
        tool_text = f"{tool['name']} {tool['description']} {tool['use_case']} {tool['category']} {' '.join(tool['tags'])}".lower()
        
        for term in query_terms:
            if term in tool_text:
                score += 1
        
        if score > 0:
            # Create a copy of the tool with the calculated score
            tool_copy = tool.copy()
            tool_copy["relevance_score"] = min(1.0, tool["relevance_score"] * (score / len(query_terms)))
            results.append(tool_copy)
    
    # Sort by relevance score and limit results
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]

async def test_ai_tools_search():
    """Test the AI tools search functionality with mock data."""
    
    # Test queries
    test_queries = [
        "find a tool to make videos from text",
        "I need something to help with coding",
        "tool for data visualization",
        "AI for content creation"
    ]
    
    # Run test queries
    logger.info("Testing AI tool search with sample queries")
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        # Search for AI tools using mock function
        results = await mock_search_ai_tools(query=query, limit=3)
        
        # Display results
        logger.info(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}:")
            logger.info(f"  Name: {result.get('name')}")
            logger.info(f"  Description: {result.get('description')}")
            logger.info(f"  Use Case: {result.get('use_case')}")
            logger.info(f"  URL: {result.get('url')}")
            logger.info(f"  Category: {result.get('category')}")
            logger.info(f"  Pricing: {result.get('pricing')}")
            logger.info(f"  Rating: {result.get('rating')}")
            logger.info(f"  Relevance Score: {result.get('relevance_score')}")
            logger.info("---")
    
    logger.info("\nTest completed successfully")

if __name__ == "__main__":
    asyncio.run(test_ai_tools_search())