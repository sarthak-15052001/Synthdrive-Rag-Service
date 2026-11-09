import asyncio
from datetime import datetime, UTC
from src.data_stores.global_tools_client import GlobalToolsClient, GlobalTool

async def test_add_tool():
    # Create test data
    tool_data = {
        "name": "ChatGPT",
        "homepage_url": "https://chat.openai.com",
        "last_scraped_at": datetime.now(UTC),
        "source_urls": ["https://openai.com/chatgpt", "https://chat.openai.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": ["Content Generation", "Conversational AI"]
        },
        "short_description": "Advanced language model for natural conversations and content creation",
        "detailed_description": "ChatGPT is an AI-powered chatbot that uses natural language processing to create human-like conversational dialogue...",
        "features": [
            {
                "name": "Natural Language Understanding",
                "description": "Understands and responds to complex queries in natural language",
                "use_case": "Customer support automation and content generation"
            },
            {
                "name": "Context Awareness",
                "description": "Maintains context throughout conversations",
                "use_case": "Extended dialogue and complex problem-solving"
            }
        ],
        "differentiators": [
            "Advanced context understanding",
            "High accuracy in natural language responses",
            "Broad knowledge base"
        ],
        "subscriptions": [
            {
                "plan_name": "Free",
                "price_monthly": None,
                "price_annual": None,
                "pricing_model": "freemium",
                "features_included": ["Basic chat functionality", "Standard response speed"]
            },
            {
                "plan_name": "Plus",
                "price_monthly": 20.0,
                "price_annual": 200.0,
                "pricing_model": "subscription",
                "features_included": ["Priority access", "Faster response speed", "Advanced features"]
            }
        ],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": True,
            "data_sovereignty_options": ["EU", "US"],
            "certifications": ["SOC2", "ISO 27001"]
        },
        "documentation_links": [
            "https://help.openai.com",
            "https://platform.openai.com/docs"
        ],
        "rating": 4.8,
        "logo_url": "https://chat.openai.com/logo.png",
        "tags": ["AI", "NLP", "Machine Learning", "Chatbot"]
    }

    try:
        # Initialize client
        client = GlobalToolsClient()
        
        # Create GlobalTool instance
        tool = GlobalTool(**tool_data)
        
        # Add the tool
        print("Adding tool to the service...")
        response = await client.add_global_tool(tool)
        
        print("Success! Response:", response)
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_add_tool())