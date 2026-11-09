import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/global/learning-resource"
HEADERS = {"Content-Type": "application/json"}

# Optional: Add authorization if needed
# If you have an API key or token, uncomment and use this
# API_KEY = "your_api_key_here"
# HEADERS["Authorization"] = f"Bearer {API_KEY}"

# Sample data for testing
test_data = {
    "title": "Introduction to RAG Systems",
    "content": "Retrieval-Augmented Generation (RAG) is an AI framework that enhances large language models by retrieving relevant information from external knowledge sources before generating responses. This approach combines the strengths of retrieval-based and generation-based methods, allowing models to access up-to-date information beyond their training data and provide more accurate, contextually relevant outputs with proper attribution to sources.",
    "url": "https://example.com/rag-introduction",
    "author": "AI Research Team",
    "resource_type": "Tutorial",
    "tags": ["RAG", "LLM", "AI", "Knowledge Retrieval"],
    "tenant_id": "default"  # Using default tenant
}

def test_ingest_global_learning_resource_api():
    """Test the global learning resource ingestion API endpoint"""
    print("Testing global learning resource ingestion API...")
    
    try:
        # Send request to the API
        response = requests.post(API_URL, json=test_data, headers=HEADERS)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            
            # Verify the response contains expected fields
            assert "job_id" in result, "Missing job_id in response"
            assert "status_code" in result, "Missing status_code in response"
            assert "status_message" in result, "Missing status_message in response"
            
            print(f"\nSuccessfully initiated global learning resource ingestion with job ID: {result.get('job_id')}")
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
    test_ingest_global_learning_resource_api()