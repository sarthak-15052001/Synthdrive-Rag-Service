import pytest
from datetime import datetime, UTC
from pydantic import HttpUrl
from src.data_stores.global_tools_client import (
    GlobalLearningResourcesClient,
    GlobalLearningResource,
    Categories,
    Content,
    TargetAudience,
    ImageAnalysis
)

@pytest.fixture
def learning_resource_client():
    return GlobalLearningResourcesClient()

@pytest.fixture
def sample_learning_resource():
    return GlobalLearningResource(
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

@pytest.mark.asyncio
async def test_post_learning_resource(learning_resource_client, sample_learning_resource):
    """Test posting a new learning resource"""
    try:
        response = await learning_resource_client.post_learning_resource(sample_learning_resource)
        assert response is not None
        # Add more specific assertions based on expected response structure
    except Exception as e:
        pytest.fail(f"Failed to post learning resource: {str(e)}")

@pytest.mark.asyncio
async def test_post_learning_resource_validation(learning_resource_client):
    """Test validation of learning resource data"""
    with pytest.raises(ValueError):
        invalid_resource = GlobalLearningResource(
            title="",  # Empty title should fail validation
            description="Test description",
            source_url=HttpUrl("https://example.com"),
            resource_type="article",
            categories=Categories(
                primary="Test",
                secondary=["Test"]
            ),
            topics_discussed=["Test"],
            target_audience=TargetAudience(
                expertise_level="beginner",
                job_roles=["Tester"]
            ),
            useful_context=["Testing"],
            content=Content(
                summary="Test summary",
                full_text="Test content"
            ),
            tags=["test"],
            estimatedTime="5 minutes",
            last_scraped_at=datetime.now(UTC)
        )
        await learning_resource_client.post_learning_resource(invalid_resource)