#!/usr/bin/env python3
"""
Test script for the comprehensive GlobalLearningResources API payload.
Tests the updated /api/v1/rag/ingest/global/learning-resource endpoint.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/rag/ingest/global/learning-resource"

# API key for authentication
API_KEY = "test-api-key-12345"

# Comprehensive payload matching the new structure
payload = {
    "title": "Introduction to ChatGPT for Marketing Teams",
    "description": "A comprehensive course on using ChatGPT to enhance marketing workflows, from content creation to customer engagement.",
    "source_url": "https://platform.example.com/courses/chatgpt-marketing",
    "resource_type": "course",
    "categories": {
        "primary": "Marketing & Sales",
        "secondary": ["Content Creation", "AI Tools", "Productivity"]
    },
    "topics_discussed": [
        "ChatGPT basics",
        "Content generation",
        "Email marketing",
        "Social media posts",
        "Customer support automation"
    ],
    "target_audience": {
        "expertise_level": "beginner",
        "job_roles": [
            "Marketing Manager",
            "Content Creator",
            "Social Media Manager",
            "Marketing Coordinator"
        ]
    },
    "useful_context": [
        "Content creation workflows",
        "Email campaign development",
        "Social media content planning",
        "Customer communication"
    ],
    "content": {
        "summary": "This course provides a comprehensive introduction to ChatGPT for marketing professionals. Learn how to leverage AI to streamline content creation, improve email campaigns, and enhance customer engagement strategies.",
        "learning_objectives": [
            "Understand ChatGPT's capabilities for marketing",
            "Create effective prompts for content generation",
            "Integrate ChatGPT into marketing workflows",
            "Generate high-quality marketing copy",
            "Automate customer communication tasks"
        ],
        "full_text_markdown": "# Introduction to ChatGPT for Marketing Teams\n\n## Overview\n\nChatGPT is a powerful AI tool that can transform how marketing teams work...\n\n## Key Features\n\n- Natural language processing\n- Content generation\n- Email automation\n- Social media assistance\n\n## Getting Started\n\n1. Sign up for ChatGPT\n2. Learn basic prompts\n3. Apply to your workflows\n\n## Conclusion\n\nChatGPT can significantly improve marketing team productivity...",
        "video_transcript": None,
        "video_url": None
    },
    "tags": [
        "chatgpt",
        "marketing",
        "ai",
        "content-creation",
        "automation"
    ],
    "estimatedTime": "4 hours",
    "platform_name": "Coursera",
    "platform_logo_url": "https://platform.example.com/logo.png",
    "associated_tool": "ChatGPT",
    "taxonomy": {
        "department": "Marketing",
        "team_task_category": "Content Creation",
        "type_category": "Text Generation"
    },
    "kpi_benefits": {
        "estimated_time_saving": "4 hours per week",
        "efficiency_gain_percentage": 40,
        "cost_reduction": "$500/month in content creation costs",
        "quality_improvement_metric": "30% increase in content engagement rates"
    },
    "is_paid": True,
    "subscriptions": {
        "plan_name": "Pro",
        "price_monthly": 49.99,
        "price_annual": 499.99,
        "pricing_model": "per_seat",
        "features_included": [
            "Full course access",
            "Certificate of completion",
            "Community forum access",
            "Lifetime updates"
        ]
    },
    "last_scraped_at": ""
}

def test_ingest_learning_resource():
    """Test ingesting a comprehensive learning resource"""
    print("=" * 80)
    print("Testing Comprehensive GlobalLearningResources Ingestion API")
    print("=" * 80)
    print(f"\nEndpoint: {API_ENDPOINT}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    print("\n" + "=" * 80)
    
    try:
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        print("\nSending request...")
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n" + "=" * 80)
            print("✓ SUCCESS: Learning resource ingestion started successfully!")
            print("=" * 80)
            print(f"Job ID: {response.json().get('job_id')}")
            print(f"Status: {response.json().get('status_message')}")
        else:
            print("\n" + "=" * 80)
            print(f"✗ ERROR: Request failed with status {response.status_code}")
            print("=" * 80)
            
    except requests.exceptions.RequestException as e:
        print("\n" + "=" * 80)
        print(f"✗ REQUEST ERROR: {str(e)}")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ UNEXPECTED ERROR: {str(e)}")
        print("=" * 80)

if __name__ == "__main__":
    test_ingest_learning_resource()
