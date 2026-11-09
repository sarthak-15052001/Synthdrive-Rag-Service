import pytest
from datetime import datetime
from src.data_stores.global_tools_client import GlobalToolsClient, GlobalTool, Feature, Categories, Subscription, Compliance

@pytest.fixture
def sample_tool_data():
    return {
        "name": "Sample AI Tool",
        "homepage_url": "https://sample-tool.com",
        "last_scraped_at": datetime.utcnow(),
        "source_urls": ["https://source1.com", "https://source2.com"],
        "categories": {
            "primary": "AI Writing",
            "secondary": ["Content Generation", "Marketing"]
        },
        "short_description": "A sample AI tool for testing",
        "detailed_description": "This is a detailed description of the sample AI tool...",
        "features": [
            {
                "name": "Feature 1",
                "description": "Description of feature 1",
                "use_case": "Example use case for feature 1"
            }
        ],
        "differentiators": [
            "Unique feature 1",
            "Unique feature 2"
        ],
        "subscriptions": [
            {
                "plan_name": "Free",
                "price_monthly": None,
                "price_annual": None,
                "pricing_model": "freemium",
                "features_included": ["Basic feature 1", "Basic feature 2"]
            }
        ],
        "compliance": {
            "gdpr_compliant": True,
            "us_cloud_act_safe": False,
            "data_sovereignty_options": ["EU", "US"],
            "certifications": ["SOC2"]
        },
        "documentation_links": [
            "https://docs.sample-tool.com/getting-started"
        ],
        "rating": 4.5,
        "logo_url": "https://sample-tool.com/logo.png",
        "tags": ["AI", "Productivity"]
    }

@pytest.mark.asyncio
async def test_add_global_tool(sample_tool_data):
    # Initialize the client
    client = GlobalToolsClient()
    
    # Create a GlobalTool instance
    tool = GlobalTool(**sample_tool_data)
    
    try:
        # Attempt to add the tool
        response = await client.add_global_tool(tool)
        
        # Verify the response
        assert response is not None
        # Add more specific assertions based on the expected response format
        
    except Exception as e:
        pytest.fail(f"Failed to add global tool: {str(e)}")

@pytest.mark.asyncio
async def test_add_global_tool_validation():
    # Initialize the client
    client = GlobalToolsClient()
    
    # Test with invalid data
    invalid_data = {
        "name": "Invalid Tool",
        # Missing required fields
    }
    
    with pytest.raises(Exception):
        tool = GlobalTool(**invalid_data)
        await client.add_global_tool(tool)