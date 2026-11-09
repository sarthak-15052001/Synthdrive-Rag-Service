import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/global/ecosystem-partner"
HEADERS = {"Content-Type": "application/json"}

# Note: The API allows unauthenticated access for development purposes
# If you have an API key or token, you can add it like this:
# API_KEY = "your_api_key_here"
# HEADERS["Authorization"] = f"Bearer {API_KEY}"

# Sample data for testing
test_data = {
    "name": "TechSolutions Inc.",
    "bio": "TechSolutions is a leading technology consulting firm specializing in AI integration, cloud migration, and digital transformation services for enterprise clients.",
    "expertise": ["AI Integration", "Cloud Migration", "Digital Transformation", "Enterprise Solutions"],
    "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional", "Microsoft Azure Expert"],
    "case_studies": "Successfully implemented AI-driven analytics platform for Fortune 500 retail client, resulting in 35% increase in operational efficiency and $2.5M annual cost savings.",
    "website": "https://techsolutions-example.com",
    "contact_info": "partners@techsolutions-example.com",
    "budget_tier": "Enterprise",
    "tags": ["AI", "Cloud", "Enterprise", "Digital Transformation"],
    "tenant_id": "default"  # Using default tenant
}

def test_ingest_global_ecosystem_partner_api():
    """Test the global ecosystem partner ingestion API endpoint"""
    print("Testing global ecosystem partner ingestion API...")
    
    try:
        # Send request to the API
        response = requests.post(API_URL, json=test_data, headers=HEADERS, timeout=60)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            
            # Verify the response contains expected fields
            assert "job_id" in result, "Missing job_id in response"
            assert "status_code" in result, "Missing status_code in response"
            assert "status_message" in result, "Missing status_message in response"
            
            print(f"\nSuccessfully initiated global ecosystem partner ingestion with job ID: {result.get('job_id')}")
            print("Test completed successfully!")
            return True
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during API test: {str(e)}")
        return False

if __name__ == "__main__":
    test_ingest_global_ecosystem_partner_api()