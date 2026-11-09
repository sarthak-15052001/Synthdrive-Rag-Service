import asyncio
from datetime import datetime, UTC
from pydantic import HttpUrl
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_stores.global_tools_client import (
    GlobalLearningResourcesClient,
    GlobalLearningResource,
    Categories,
    Content,
    TargetAudience,
    ImageAnalysis
)

async def test_post_learning_resource():
    client = GlobalLearningResourcesClient()
    
    # Create a sample learning resource
    resource = GlobalLearningResource(
        title="Introduction to AI Ethics",
        description="A comprehensive guide to ethical considerations in artificial intelligence development",
        source_url=HttpUrl("https://example.com/ai-ethics-guide"),
        resource_type="article",
        categories=Categories(
            primary="AI Ethics",
            secondary=["Responsible AI", "AI Governance"]
        ),
        topics_discussed=["Bias in AI", "Transparency", "Accountability", "Privacy"],
        target_audience=TargetAudience(
            expertise_level="intermediate",
            job_roles=["Data Scientist", "AI Engineer", "Product Manager"]
        ),
        useful_context=["AI Development", "Policy Creation", "Team Training"],
        content=Content(
            summary="This article provides a comprehensive overview of ethical considerations in AI development, including bias mitigation, transparency requirements, and governance frameworks.",
            full_text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...",
            image_analysis=[
                ImageAnalysis(
                    image_url=HttpUrl("https://example.com/images/ai-ethics-diagram.png"),
                    description="Diagram showing the relationship between various ethical considerations in AI development"
                )
            ]
        ),
        tags=["ethics", "ai", "governance", "bias", "transparency"],
        estimatedTime="15 minutes",
        last_scraped_at=datetime.now(UTC)
    )
    
    try:
        print("Posting learning resource...")
        response = await client.post_learning_resource(resource)
        print("Success! Response:", response)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_post_learning_resource())