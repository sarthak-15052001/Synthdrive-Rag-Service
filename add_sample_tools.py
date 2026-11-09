import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_stores.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def add_sample_tools():
    """
    Add sample AI tools to the Weaviate database.
    """
    # Initialize the Weaviate client
    # Get Weaviate URL from environment variables or use default
    weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    weaviate_client = WeaviateClient(weaviate_url=weaviate_url)
    
    # Sample AI tools data
    sample_tools = [
        {
            "name": "Synthesia",
            "description": "AI video generation platform that turns text into professional videos with virtual presenters.",
            "use_case": "Create professional videos from text scripts with AI avatars speaking your content.",
            "url": "https://www.synthesia.io/",
            "category": "Video Generation",
            "pricing": "Free trial, then paid plans starting at $30/month",
            "reviews": "Users praise the ease of use and quality of AI presenters.",
            "rating": 4.5,
            "tags": ["video", "content creation", "AI presenter", "text-to-video"],
            "tool_id": "synthesia-001"
        },
        {
            "name": "Descript",
            "description": "All-in-one audio and video editing platform with AI-powered features like text-based editing and voice cloning.",
            "use_case": "Edit videos by editing text, create voice overs with AI voices, and streamline video production.",
            "url": "https://www.descript.com/",
            "category": "Video Editing",
            "pricing": "Free plan available, paid plans from $12/month",
            "reviews": "Highly rated for innovative text-based editing approach.",
            "rating": 4.7,
            "tags": ["video editing", "audio editing", "text-to-video", "voice cloning"],
            "tool_id": "descript-001"
        },
        {
            "name": "Runway",
            "description": "AI-powered creative suite for video editing, generation, and visual effects.",
            "use_case": "Create and edit videos with AI, generate new videos from text, and apply advanced visual effects.",
            "url": "https://runwayml.com/",
            "category": "Video Creation",
            "pricing": "Free trial, then paid plans starting at $15/month",
            "reviews": "Popular among creators for its powerful AI video generation capabilities.",
            "rating": 4.6,
            "tags": ["video generation", "visual effects", "text-to-video", "AI editing"],
            "tool_id": "runway-001"
        },
        {
            "name": "Lumen5",
            "description": "Video creation platform that turns blog posts and text content into engaging videos.",
            "use_case": "Convert blog posts, articles, and text content into social media videos with minimal effort.",
            "url": "https://lumen5.com/",
            "category": "Content Repurposing",
            "pricing": "Free plan available, paid plans from $19/month",
            "reviews": "Great for content marketers looking to repurpose written content as videos.",
            "rating": 4.3,
            "tags": ["content repurposing", "social media", "text-to-video", "marketing"],
            "tool_id": "lumen5-001"
        },
        {
            "name": "Elai.io",
            "description": "AI video generation platform that creates videos from text with customizable AI presenters.",
            "use_case": "Create explainer videos, product demos, and training content from text scripts.",
            "url": "https://elai.io/",
            "category": "Video Generation",
            "pricing": "Free trial, then paid plans starting at $29/month",
            "reviews": "Users appreciate the multilingual capabilities and ease of use.",
            "rating": 4.2,
            "tags": ["video generation", "AI presenter", "text-to-video", "training"],
            "tool_id": "elai-001"
        },
        {
            "name": "ChatGPT",
            "description": "Conversational AI assistant that can answer questions, generate content, and assist with various tasks.",
            "use_case": "Get answers to questions, generate content, brainstorm ideas, and automate writing tasks.",
            "url": "https://chat.openai.com/",
            "category": "AI Assistant",
            "pricing": "Free tier available, ChatGPT Plus at $20/month",
            "reviews": "Widely used for its versatility and powerful language capabilities.",
            "rating": 4.8,
            "tags": ["AI assistant", "content generation", "writing", "research"],
            "tool_id": "chatgpt-001"
        },
        {
            "name": "Midjourney",
            "description": "AI art generation tool that creates stunning images from text descriptions.",
            "use_case": "Generate artwork, illustrations, and visual concepts from text prompts.",
            "url": "https://www.midjourney.com/",
            "category": "Image Generation",
            "pricing": "Subscription plans starting at $10/month",
            "reviews": "Known for high-quality, artistic image generation capabilities.",
            "rating": 4.9,
            "tags": ["AI art", "image generation", "text-to-image", "creative"],
            "tool_id": "midjourney-001"
        }
    ]
    
    # Add each tool to Weaviate
    for tool in sample_tools:
        try:
            # Add the tool to Weaviate
            weaviate_client.add_ai_tool(
                name=tool["name"],
                description=tool["description"],
                use_case=tool["use_case"],
                url=tool["url"],
                category=tool["category"],
                pricing=tool["pricing"],
                reviews=tool["reviews"],
                rating=tool["rating"],
                tags=tool["tags"],
                tool_id=tool["tool_id"]
            )
            logger.info(f"Added tool: {tool['name']}")
        except Exception as e:
            logger.error(f"Error adding tool {tool['name']}: {str(e)}")
    
    logger.info("Finished adding sample tools")

if __name__ == "__main__":
    add_sample_tools()