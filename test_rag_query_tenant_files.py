import requests
import json
import logging
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rag_query_with_tenant_files():
    """
    Test the RAG query API endpoint with tenant files.
    
    This function sends test queries to the /api/v1/rag/query endpoint
    with filters specific to tenant files and processes the streaming response.
    """
    # API endpoint
    api_url = "http://localhost:8000/api/v1/rag/query"
    
    # Authorization header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"
    }
    
    logger.info("Testing RAG query API endpoint with tenant files")
    
    # Test cases with different parameters
    test_cases = [
        {
            "name": "Query for business strategy documents",
            "payload": {
                "query_str": "What are the key business objectives for 2023?",
                "tenant_id": "default",
                "filters": {
                    "tags": ["business", "strategy"],
                    "organization_id": "test_org_123"
                },
                "top_k": 5
            }
        },
        {
            "name": "Query for financial performance insights",
            "payload": {
                "query_str": "Summarize the financial growth and revenue trends in 2023.",
                "tenant_id": "default",
                "filters": {
                    "file_type": "pdf",
                    "tags": ["financial", "2023"]
                },
                "top_k": 5
            }
        },
        {
            "name": "Query for marketing strategy details",
            "payload": {
                "query_str": "Explain the digital marketing focus areas for 2023.",
                "tenant_id": "default",
                "filters": {
                    "file_path": "/marketing/strategy/2023.docx",
                    "tags": ["marketing", "strategy"]
                },
                "top_k": 5
            }
        },
        {
            "name": "Query for product roadmap updates",
            "payload": {
                "query_str": "What are the upcoming product launches planned for 2023-2024?",
                "tenant_id": "default",
                "filters": {
                    "tags": ["product", "roadmap"],
                    "organization_id": "test_org_123"
                },
                "top_k": 5
            }
        },
        {
            "name": "Query for annual company performance summary",
            "payload": {
                "query_str": "Give an overview of the 2023 annual report highlights.",
                "tenant_id": "default",
                "filters": {
                    "file_name": "Annual Report 2023.pdf",
                    "tags": ["annual", "report"]
                },
                "top_k": 5
            }
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST CASE: {test_case['name']}")
        logger.info(f"{'='*60}")
        logger.info(f"Query: {test_case['payload']['query_str']}")
        logger.info(f"Filters: {json.dumps(test_case['payload'].get('filters', {}), indent=2)}")
        
        try:
            # Make the request with stream=True to handle SSE
            response = requests.post(api_url, json=test_case['payload'], headers=headers, stream=True)
            
            # Check if request was successful
            if response.status_code != 200:
                logger.error(f"Error: Received status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                continue
            
            # Process the streaming response
            logger.info("Streaming response:")
            
            answer = None
            citations = []
            reasoning = None
            synthesis = None
            
            for line in response.iter_lines():
                if line:
                    # SSE format: data: {...}
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_json = line_text[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_json)
                            
                            # Process different parts of the response
                            if 'answer' in data:
                                answer = data['answer']
                                logger.info(f"Answer: {answer}")
                            
                            if 'citations' in data:
                                citations = data['citations']
                                logger.info(f"Citations: {len(citations)} sources")
                                for i, citation in enumerate(citations):
                                    logger.info(f"  Citation {i+1}:")
                                    logger.info(f"    Source: {citation.get('source', 'Unknown')}")
                                    logger.info(f"    Content: {citation.get('content', '')[:100]}...")
                                    if 'metadata' in citation and citation['metadata']:
                                        logger.info(f"    Metadata: {citation['metadata']}")
                            
                            if 'reasoning' in data:
                                reasoning = data['reasoning']
                                if reasoning:
                                    logger.info(f"Reasoning: {reasoning[:100]}...")
                                else:
                                    logger.info(f"Reasoning: No reasoning provided.")
                            
                            if 'synthesis' in data:
                                synthesis = data['synthesis']
                                if synthesis:
                                    logger.info(f"Synthesis: {synthesis[:100]}...")
                                else:
                                    logger.info(f"Synthesis: No synthesis provided.")
                            
                            if 'error' in data:
                                logger.error(f"Error in response: {data['error']}")
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON: {e}")
                            logger.error(f"Raw data: {data_json}")
            
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"Error making request: {str(e)}")
    
    logger.info("\nTest completed")

def save_tenant_file_payloads():
    """
    Save sample tenant file query payloads to files for reference and testing.
    """
    sample_payloads = [
        {
            "filename": "business_strategy_query.json",
            "payload": {
                "query_str": "What are the key business objectives for 2023?",
                "tenant_id": "default",
                "filters": {
                    "tags": ["business", "strategy"],
                    "organization_id": "test_org_123"
                },
                "top_k": 5
            }
        },
        {
            "filename": "financial_performance_query.json",
            "payload": {
                "query_str": "Summarize the financial growth and revenue trends in 2023.",
                "tenant_id": "default",
                "filters": {
                    "file_type": "pdf",
                    "tags": ["financial", "2023"]
                },
                "top_k": 5
            }
        },
        {
            "filename": "marketing_strategy_query.json",
            "payload": {
                "query_str": "Explain the digital marketing focus areas for 2023.",
                "tenant_id": "default",
                "filters": {
                    "file_path": "/marketing/strategy/2023.docx",
                    "tags": ["marketing", "strategy"]
                },
                "top_k": 5
            }
        },
        {
            "filename": "product_roadmap_query.json",
            "payload": {
                "query_str": "What are the upcoming product launches planned for 2023-2024?",
                "tenant_id": "default",
                "filters": {
                    "tags": ["product", "roadmap"],
                    "organization_id": "test_org_123"
                },
                "top_k": 5
            }
        },
        {
            "filename": "annual_report_query.json",
            "payload": {
                "query_str": "Give an overview of the 2023 annual report highlights.",
                "tenant_id": "default",
                "filters": {
                    "file_name": "Annual Report 2023.pdf",
                    "tags": ["annual", "report"]
                },
                "top_k": 5
            }
        }
    ]
    
    # Create directory for sample payloads
    import os
    os.makedirs("tenant_file_payloads", exist_ok=True)
    
    # Save each payload to a file
    for sample in sample_payloads:
        filepath = os.path.join("tenant_file_payloads", sample["filename"])
        with open(filepath, "w") as f:
            json.dump(sample["payload"], f, indent=2)
        logger.info(f"Saved sample tenant file payload to {filepath}")

if __name__ == "__main__":
    # Save sample payloads first
    save_tenant_file_payloads()
    
    # Run the tests
    test_rag_query_with_tenant_files()