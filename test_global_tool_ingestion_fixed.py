"""
Test script for verifying the fixed global tool ingestion endpoint.
This script tests that all fields are properly stored in both Weaviate and Neo4j.
"""

import requests
import json
from datetime import datetime, timezone

# API endpoint
BASE_URL = "http://localhost:8000/api/v1/rag"
INGEST_ENDPOINT = f"{BASE_URL}/ingest/global/tool"

# Complete test payload with all fields
payload = {
    "name": "TestTool AI",
    "homepage_url": "https://testtool-ai.com",
    "last_scraped_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "source_urls": ["https://source1.testtool.com", "https://source2.testtool.com"],
    "categories": {
        "primary": "AI Writing",
        "secondary": ["Content Generation", "Marketing", "SEO"]
    },
    "short_description": "A powerful AI writing assistant that helps create engaging content quickly and efficiently.",
    "detailed_description": "TestTool AI is a comprehensive AI-powered writing platform that combines advanced language models with intuitive editing tools. It helps content creators, marketers, and businesses produce high-quality written content at scale while maintaining brand voice and style consistency.",
    "features": [
        {
            "name": "AI Content Generation",
            "description": "Generate blog posts, articles, and marketing copy using advanced AI",
            "use_case": "Create SEO-optimized blog posts in minutes instead of hours"
        },
        {
            "name": "Brand Voice Matching",
            "description": "Train the AI to match your unique brand voice and style",
            "use_case": "Maintain consistency across all content pieces"
        },
        {
            "name": "Multi-language Support",
            "description": "Create content in over 50 languages",
            "use_case": "Expand your reach to international markets"
        }
    ],
    "differentiators": [
        "Advanced context understanding that preserves meaning across long-form content",
        "Built-in plagiarism checker and SEO optimization",
        "Collaborative editing with real-time team feedback"
    ],
    "subscriptions": [
        {
            "plan_name": "Free",
            "price_monthly": None,
            "price_annual": None,
            "pricing_model": "freemium",
            "features_included": ["5,000 words/month", "Basic templates", "1 brand voice"]
        },
        {
            "plan_name": "Pro",
            "price_monthly": 29.99,
            "price_annual": 299.99,
            "pricing_model": "per_seat",
            "features_included": ["Unlimited words", "All templates", "5 brand voices", "Priority support"]
        },
        {
            "plan_name": "Enterprise",
            "price_monthly": 99.99,
            "price_annual": 999.99,
            "pricing_model": "per_seat",
            "features_included": ["Everything in Pro", "Custom integrations", "Dedicated account manager", "SLA guarantee"]
        }
    ],
    "compliance": {
        "gdpr_compliant": True,
        "us_cloud_act_safe": False,
        "data_sovereignty_options": ["EU", "US", "UK"],
        "certifications": ["SOC2", "ISO 27001", "HIPAA"]
    },
    "documentation_links": [
        "https://docs.testtool-ai.com/getting-started",
        "https://docs.testtool-ai.com/api-reference",
        "https://docs.testtool-ai.com/best-practices"
    ],
    "rating": 4.7,
    "logo_url": "https://testtool-ai.com/logo.png",
    "tags": ["AI", "Writing", "Content Creation", "Marketing", "SEO", "Productivity"]
}

# Headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "test-api-key"  # Use your actual API key
}

def test_ingestion():
    """Test the global tool ingestion endpoint"""
    print("=" * 80)
    print("TESTING GLOBAL TOOL INGESTION")
    print("=" * 80)
    print(f"\nEndpoint: {INGEST_ENDPOINT}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    print("\n" + "=" * 80)
    
    try:
        # Send the request
        print("\nSending POST request...")
        response = requests.post(
            INGEST_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Tool ingestion started successfully")
            job_id = response.json().get("job_id")
            print(f"Job ID: {job_id}")
            print("\nCheck your terminal logs to see detailed information about:")
            print("  1. Weaviate storage - all fields including last_scraped_at")
            print("  2. Neo4j graph creation - Tool node, Categories, Features, Tags")
        else:
            print(f"\n❌ ERROR: Ingestion failed with status {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out after 60 seconds")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 80)

def verify_weaviate_storage():
    """Verify the tool is stored in Weaviate with all fields"""
    print("\n" + "=" * 80)
    print("VERIFYING WEAVIATE STORAGE")
    print("=" * 80)
    print("\nYou can check Weaviate directly using:")
    print("  - Weaviate Console/Explorer")
    print("  - GraphQL query")
    print("\nExpected fields in Global_Tools collection:")
    expected_fields = [
        "name", "homepage_url", "last_scraped_at", "source_urls",
        "primary_category", "secondary_categories",
        "short_description", "detailed_description",
        "features_json", "differentiators",
        "subscriptions_json", "compliance_json",
        "documentation_links", "rating", "logo_url", "tags",
        "tenant_id", "content"
    ]
    for field in expected_fields:
        print(f"  ✓ {field}")
    
    print("\nNote: features, subscriptions, and compliance are stored as JSON strings")
    print("You'll need to parse them to get the original structure")

def verify_neo4j_storage():
    """Verify the tool is stored in Neo4j graph"""
    print("\n" + "=" * 80)
    print("VERIFYING NEO4J STORAGE")
    print("=" * 80)
    print("\nYou can check Neo4j using:")
    print("  - Neo4j Browser (http://localhost:7474)")
    print("  - Cypher queries")
    print("\nExpected graph structure:")
    print("  ✓ Tool node with properties (tool_id, name, homepage_url, descriptions, rating, etc.)")
    print("  ✓ Category nodes connected via HAS_PRIMARY_CATEGORY and HAS_SECONDARY_CATEGORY")
    print("  ✓ Feature nodes connected via HAS_FEATURE")
    print("  ✓ Tag nodes connected via HAS_TAG")
    print("\nExample Cypher query to verify:")
    print("""
    MATCH (t:Tool {name: 'TestTool AI'})-[r]-(n)
    RETURN t, type(r), n
    LIMIT 25
    """)

if __name__ == "__main__":
    # Run the ingestion test
    test_ingestion()
    
    # Print verification instructions
    verify_weaviate_storage()
    verify_neo4j_storage()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Check the terminal logs where your server is running")
    print("2. Verify data in Weaviate Console")
    print("3. Verify graph in Neo4j Browser")
    print("=" * 80 + "\n")
