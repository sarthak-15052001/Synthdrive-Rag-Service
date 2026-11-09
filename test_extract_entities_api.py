import requests
import json
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/extract-entities-relations"
HEADERS = {"Content-Type": "application/json"}

# Sample data for testing
test_data = {
    "file_id": "test-file-123",
    "organization_id": "test-org-456",
    "tenant_id": "default",
    "raw_text": """
    SynthDrive Inc. is working on a new AI project called Project Horizon. 
    The project is led by Dr. Sarah Johnson, who joined the company in 2023.
    The team is using OpenAI's GPT-4 and Google's BERT models for natural language processing tasks.
    They are collaborating with Microsoft on cloud infrastructure.
    The project deadline is December 15, 2025, and they plan to present at the AI Summit in San Francisco.
    """,
    "status": "processing",
    "processing_log": [f"Test started at {datetime.now().isoformat()}"]
}

def test_extract_entities_api():
    """Test the entity extraction API endpoint"""
    print("Testing entity extraction API...")
    
    try:
        # Send request to the API
        response = requests.post(API_URL, json=test_data, headers=HEADERS)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            
            # Verify the response contains expected fields
            assert "file_id" in result, "Missing file_id in response"
            assert "organization_id" in result, "Missing organization_id in response"
            assert "entities_and_relations" in result, "Missing entities_and_relations in response"
            assert "status" in result, "Missing status in response"
            
            # Check if entities were extracted
            entities = result.get("entities_and_relations", {}).get("entities", [])
            relationships = result.get("entities_and_relations", {}).get("relationships", [])
            
            print(f"\nExtracted {len(entities)} entities and {len(relationships)} relationships")
            
            if entities:
                print("\nEntities:")
                for entity in entities:
                    print(f"- {entity.get('name')} ({entity.get('type')})")
            
            if relationships:
                print("\nRelationships:")
                for rel in relationships:
                    print(f"- {rel.get('source_id')} -> {rel.get('target_id')} ({rel.get('type')})")
            
            print("\nTest completed successfully!")
            return True
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during API test: {str(e)}")
        return False

if __name__ == "__main__":
    test_extract_entities_api()