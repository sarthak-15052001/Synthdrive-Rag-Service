#!/usr/bin/env python3
"""
Script to add sample AI tools to the Global_Tools collection for testing the RAG tools search API.

This script adds a set of sample AI tools to the Weaviate database to allow for proper testing
of the /api/v1/rag/tools/search API endpoint.
"""

import logging
import sys
import uuid
from datetime import datetime, timezone
from src.data_stores.weaviate_client import WeaviateClient

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def add_sample_tools():
    """Add sample AI tools to the Global_Tools collection."""
    print("Starting add_sample_tools...")
    try:
        # Initialize Weaviate client
        print("Initializing Weaviate client...")
        weaviate_client = WeaviateClient()
        print("Weaviate client initialized successfully")
        
        # Check initial count
        print("Checking initial count of objects in Global_Tools...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        print(f"Aggregate result: {result}")
        
        initial_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            initial_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"Initial count of objects in Global_Tools: {initial_count}")
        
        # Sample tools data
        sample_tools = [
            {
                "name": "Synthesia",
                "description": "AI video generation platform that turns text into videos with virtual avatars",
                "use_case": "Creating professional-looking videos without filming",
                "url": "https://www.synthesia.io/",
                "category": "Video Creation",
                "pricing": "Free trial, then paid plans starting at $30/month",
                "reviews": "Users praise the ease of use and quality of videos",
                "rating": 4.7,
                "tags": ["video", "ai", "text-to-video"]
            },
            {
                "name": "Descript",
                "description": "All-in-one audio and video editing platform with AI transcription and voice cloning",
                "use_case": "Editing podcasts and videos by editing text",
                "url": "https://www.descript.com/",
                "category": "Video Editing",
                "pricing": "Free plan available, paid plans from $12/month",
                "reviews": "Highly rated for its innovative text-based editing approach",
                "rating": 4.6,
                "tags": ["video", "audio", "editing", "transcription"]
            },
            {
                "name": "GitHub Copilot",
                "description": "AI pair programmer that suggests code completions based on context",
                "use_case": "Accelerating software development with AI code suggestions",
                "url": "https://github.com/features/copilot",
                "category": "Development",
                "pricing": "$10/month for individuals, $19/user/month for businesses",
                "reviews": "Developers report significant productivity improvements",
                "rating": 4.8,
                "tags": ["coding", "programming", "development", "ai"]
            },
            {
                "name": "Jasper",
                "description": "AI content generation platform for marketing copy and creative content",
                "use_case": "Creating marketing content, blog posts, and social media copy",
                "url": "https://www.jasper.ai/",
                "category": "Content Creation",
                "pricing": "Plans start at $49/month",
                "reviews": "Marketing teams praise the quality and variety of content it produces",
                "rating": 4.5,
                "tags": ["writing", "marketing", "content"]
            },
            {
                "name": "Midjourney",
                "description": "AI art generation tool that creates images from text descriptions",
                "use_case": "Creating unique artwork and illustrations for various projects",
                "url": "https://www.midjourney.com/",
                "category": "Image Generation",
                "pricing": "Basic plan starts at $10/month",
                "reviews": "Artists and designers love the creative possibilities",
                "rating": 4.9,
                "tags": ["image", "art", "design", "ai"]
            },
            {
                "name": "Tableau",
                "description": "Data visualization software that helps people see and understand data",
                "use_case": "Creating interactive dashboards and data visualizations",
                "url": "https://www.tableau.com/",
                "category": "Data Visualization",
                "pricing": "Plans start at $70/user/month",
                "reviews": "Business analysts rate it highly for its powerful visualization capabilities",
                "rating": 4.5,
                "tags": ["data", "visualization", "analytics", "business intelligence"]
            },
            {
                "name": "ChatGPT",
                "description": "Conversational AI assistant that can answer questions and generate content",
                "use_case": "Customer support, content creation, and research assistance",
                "url": "https://chat.openai.com/",
                "category": "Conversational AI",
                "pricing": "Free tier available, ChatGPT Plus at $20/month",
                "reviews": "Users appreciate its versatility and knowledge breadth",
                "rating": 4.7,
                "tags": ["chatbot", "ai", "assistant", "nlp"]
            },
            {
                "name": "Notion AI",
                "description": "AI writing assistant integrated with the Notion workspace",
                "use_case": "Drafting documents, summarizing content, and generating ideas",
                "url": "https://www.notion.so/product/ai",
                "category": "Productivity",
                "pricing": "$10/month on top of Notion subscription",
                "reviews": "Users highlight its seamless integration with Notion workspace",
                "rating": 4.4,
                "tags": ["writing", "productivity", "workspace", "ai"]
            },
            {
                "name": "Canva",
                "description": "Design platform with AI features for creating graphics and presentations",
                "use_case": "Creating marketing materials, social media graphics, and presentations",
                "url": "https://www.canva.com/",
                "category": "Design",
                "pricing": "Free tier available, Pro plan at $12.99/month",
                "reviews": "Non-designers appreciate its ease of use and professional results",
                "rating": 4.8,
                "tags": ["design", "graphics", "marketing", "presentations"]
            },
            {
                "name": "Grammarly",
                "description": "AI writing assistant that checks grammar, spelling, and writing style",
                "use_case": "Improving writing quality across documents, emails, and web content",
                "url": "https://www.grammarly.com/",
                "category": "Writing",
                "pricing": "Free tier available, Premium from $12/month",
                "reviews": "Writers and professionals value its comprehensive feedback",
                "rating": 4.7,
                "tags": ["writing", "grammar", "editing", "proofreading"]
            }
        ]
        
        # Add each tool
        added_count = 0
        for tool in sample_tools:
            try:
                # Generate a unique tool_id if not present
                if "tool_id" not in tool:
                    tool["tool_id"] = str(uuid.uuid4())
                
                # Add the tool
                print(f"Adding tool: {tool['name']}...")
                tool_id = weaviate_client.add_global_tool(tool, tenant_id="default")
                print(f"Added tool {tool['name']} with ID: {tool_id}")
                added_count += 1
            except Exception as e:
                print(f"Error adding tool {tool.get('name', 'unknown')}: {str(e)}")
        
        # Check final count
        print("Checking final count of objects in Global_Tools...")
        result = weaviate_client.client.query.aggregate("Global_Tools").with_meta_count().do()
        
        final_count = 0
        if result and "data" in result and "Aggregate" in result["data"] and "Global_Tools" in result["data"]["Aggregate"]:
            final_count = result["data"]["Aggregate"]["Global_Tools"][0]["meta"]["count"]
        
        print(f"Final count of objects in Global_Tools: {final_count}")
        print(f"Added {added_count} sample tools successfully")
        
        # Verify by retrieving some tools
        print("Retrieving sample tools to verify...")
        results = weaviate_client.search_ai_tools("AI tools", limit=5)
        
        if results:
            print(f"Successfully retrieved {len(results)} tools:")
            for i, tool in enumerate(results, 1):
                print(f"{i}. {tool.get('name')} - {tool.get('description')}")
        else:
            print("No tools retrieved. There might be an issue with the search functionality.")
        
    except Exception as e:
        print(f"Error adding sample tools: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    add_sample_tools()