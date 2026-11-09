#!/usr/bin/env python3
"""
Test script to verify the learning resource fix in Weaviate.
This script tests that:
1. Data is saved only once (no duplicates)
2. Nested structures (categories, target_audience) are properly maintained
3. Null values for video_transcript and video_url are handled correctly
"""

import requests
import json
import time

# API endpoint
API_URL = "http://localhost:8000/api/v1/rag/ingest/global/learning-resource"

# Test payload with all fields including nulls
test_payload = {
    "title": "Introduction to AI Ethics",
    "description": "A comprehensive guide to ethical considerations in artificial intelligence development",
    "source_url": "https://example.com/ai-ethics-guide",
    "resource_type": "article",
    "categories": {
        "primary": "AI Ethics",
        "secondary": ["Responsible AI", "AI Governance"]
    },
    "topics_discussed": ["Bias in AI", "Transparency", "Accountability", "Privacy"],
    "target_audience": {
        "expertise_level": "intermediate",
        "job_roles": ["Data Scientist", "AI Engineer", "Product Manager"]
    },
    "useful_context": ["AI Development", "Policy Creation", "Team Training"],
    "content": {
        "summary": "This article provides a comprehensive overview of ethical considerations in AI development, including bias mitigation, transparency requirements, and governance frameworks.",
        "full_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua...",
        "video_transcript": None,  # Testing null value
        "video_url": None,  # Testing null value
        "image_analysis": [
            {
                "image_url": "https://example.com/images/ai-ethics-diagram.png",
                "description": "Diagram showing the relationship between various ethical considerations in AI development"
            }
        ]
    },
    "tags": ["ethics", "ai", "governance", "bias", "transparency"],
    "estimatedTime": "15 minutes",
    "last_scraped_at": ""
}

def test_ingestion():
    """Test the ingestion endpoint"""
    print("=" * 80)
    print("Testing Learning Resource Ingestion")
    print("=" * 80)
    
    # Send the request
    print("\nSending POST request to:", API_URL)
    print("\nPayload:")
    print(json.dumps(test_payload, indent=2))
    
    try:
        response = requests.post(
            API_URL,
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n" + "=" * 80)
        print("Response Status Code:", response.status_code)
        print("=" * 80)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Success! Response:")
            print(json.dumps(result, indent=2))
            
            print("\n" + "=" * 80)
            print("Verification Steps:")
            print("=" * 80)
            print("1. Check Weaviate Cloud Console")
            print("2. Navigate to Global_LearningResources class")
            print("3. Look for the resource with title: 'Introduction to AI Ethics'")
            print("4. Verify the following:")
            print("   - Data appears only ONCE (no duplicates)")
            print("   - 'primary_category' field contains: 'AI Ethics'")
            print("   - 'secondary_categories' field contains: ['Responsible AI', 'AI Governance']")
            print("   - NO separate 'primary' or 'secondary' fields outside categories")
            print("   - 'expertise_level' field contains: 'intermediate'")
            print("   - 'job_roles' field contains: ['Data Scientist', 'AI Engineer', 'Product Manager']")
            print("   - NO separate fields like 'job_roles' duplicating the data")
            print("   - 'video_transcript' field shows: null")
            print("   - 'video_url' field shows: null")
            
        else:
            print("\n✗ Error! Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ Error during request: {str(e)}")
        import traceback
        traceback.print_exc()

def verify_weaviate_direct():
    """
    Optional: Direct verification using Weaviate client
    Uncomment if you want to verify programmatically
    """
    try:
        from src.data_stores.weaviate_client import WeaviateClient
        from src.core.config import settings
        
        print("\n" + "=" * 80)
        print("Direct Weaviate Verification")
        print("=" * 80)
        
        client = WeaviateClient()
        
        # Query for the resource
        result = client.client.query.get(
            "Global_LearningResources",
            [
                "title", "description", "source_url", "resource_type",
                "primary_category", "secondary_categories", "topics_discussed",
                "expertise_level", "job_roles", "useful_context",
                "summary", "full_text", "video_transcript", "video_url",
                "image_urls", "image_descriptions", "tags",
                "estimated_time", "last_scraped_at", "resource_id", "tenant_id"
            ]
        ).with_where({
            "path": ["title"],
            "operator": "Equal",
            "valueString": "Introduction to AI Ethics"
        }).with_limit(5).do()
        
        if result and "data" in result and "Get" in result["data"]:
            resources = result["data"]["Get"]["Global_LearningResources"]
            
            print(f"\n✓ Found {len(resources)} resource(s) in Weaviate")
            
            if len(resources) > 1:
                print("\n⚠️  WARNING: Multiple resources found! This indicates duplicate data.")
            
            for idx, resource in enumerate(resources, 1):
                print(f"\n--- Resource #{idx} ---")
                print(f"Title: {resource.get('title')}")
                print(f"Primary Category: {resource.get('primary_category')}")
                print(f"Secondary Categories: {resource.get('secondary_categories')}")
                print(f"Expertise Level: {resource.get('expertise_level')}")
                print(f"Job Roles: {resource.get('job_roles')}")
                print(f"Video Transcript: {resource.get('video_transcript')}")
                print(f"Video URL: {resource.get('video_url')}")
                
                # Check for unwanted fields (if they exist, it's a problem)
                all_keys = list(resource.keys())
                problematic_keys = []
                if 'primary' in all_keys:
                    problematic_keys.append('primary')
                if 'secondary' in all_keys:
                    problematic_keys.append('secondary')
                
                if problematic_keys:
                    print(f"\n⚠️  WARNING: Found flattened category fields: {problematic_keys}")
                    print("   This indicates the structure is not being maintained correctly.")
                else:
                    print("\n✓ Structure looks correct - no flattened fields detected")
        else:
            print("\n✗ No resources found in Weaviate")
            
    except Exception as e:
        print(f"\n⚠️  Could not perform direct Weaviate verification: {str(e)}")
        print("   This is optional - please verify manually in Weaviate Cloud Console")

if __name__ == "__main__":
    # Test the ingestion
    test_ingestion()
    
    # Wait a bit for data to be persisted
    print("\n\nWaiting 5 seconds for data to be persisted...")
    time.sleep(5)
    
    # Try direct verification (optional)
    print("\n")
    try:
        verify_weaviate_direct()
    except:
        pass
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print("\nPlease check the Weaviate Cloud Console to verify:")
    print("1. Only ONE entry exists for 'Introduction to AI Ethics'")
    print("2. The 'primary_category' and 'secondary_categories' fields exist")
    print("3. No separate 'primary' or 'secondary' fields exist")
    print("4. The 'video_transcript' and 'video_url' fields show as null/None")
    print("=" * 80)
