import json
import requests
from datetime import datetime, timezone

# Configuration
API_URL = "http://localhost:8000/api/v1/rag/ingest/persist-to-neo4j"
API_KEY = "your_api_key_here"  # Replace with your actual API key

def test_persist_to_neo4j():
    """
    Test the persist_to_neo4j API endpoint.
    """
    # Sample data with entities and relations
    payload = {
        "file_id": "test-file-123",
        "organization_id": "test-org-456",
        "tenant_id": "default",
        "entities_and_relations": {
            "entities": [
                {
                    "id": "entity-1",
                    "name": "John Doe",
                    "type": "PERSON"
                },
                {
                    "id": "entity-2",
                    "name": "Acme Corporation",
                    "type": "ORGANIZATION"
                },
                {
                    "id": "entity-3",
                    "name": "Project Alpha",
                    "type": "PROJECT"
                }
            ],
            "relationships": [
                {
                    "source": "John Doe",
                    "target": "Acme Corporation",
                    "type": "WORKS_FOR"
                },
                {
                    "source": "John Doe",
                    "target": "Project Alpha",
                    "type": "MANAGES"
                },
                {
                    "source": "Acme Corporation",
                    "target": "Project Alpha",
                    "type": "OWNS"
                }
            ]
        },
        "status": "entities_extracted",
        "processing_log": [
            f"Entity extraction completed at {datetime.now(timezone.utc).isoformat()}"
        ]
    }

    # Set headers with API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Make the API request
    response = requests.post(API_URL, json=payload, headers=headers)

    # Print the response
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response

if __name__ == "__main__":
    test_persist_to_neo4j()