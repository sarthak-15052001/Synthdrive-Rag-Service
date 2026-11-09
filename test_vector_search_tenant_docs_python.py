"""
Test script for the /api/v1/rag/vector-search-tenant-docs API endpoint using Python requests.

This script tests the API with the 5 payloads provided in the task.
"""
import requests
import json
import logging
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Set the API endpoint URL
API_URL = "http://localhost:8001/api/v1/rag/vector-search-tenant-docs"

# Set the headers
HEADERS = {
    "Content-Type": "application/json"
}

def test_payload(payload_name, payload):
    """Test a payload against the API endpoint."""
    logger.info(f"{Fore.YELLOW}Testing Payload {payload_name}:{Style.RESET_ALL}")
    logger.info(json.dumps(payload, indent=2))
    logger.info("")
    
    try:
        # Make the API request
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()
            
            logger.info(f"{Fore.GREEN}Response:{Style.RESET_ALL}")
            logger.info(json.dumps(result, indent=2))
            
            # Check if the response contains the expected fields
            if "query" in result and "organization_id" in result and "files" in result:
                logger.info(f"{Fore.GREEN}✓ Response contains the expected fields{Style.RESET_ALL}")
                
                # Check if the organization_id is correct
                org_id = payload["organization_id"]
                resp_org_id = result["organization_id"]
                if org_id == resp_org_id:
                    logger.info(f"{Fore.GREEN}✓ organization_id is correct: {resp_org_id}{Style.RESET_ALL}")
                else:
                    logger.info(f"{Fore.RED}✗ organization_id is incorrect: expected {org_id}, got {resp_org_id}{Style.RESET_ALL}")
                
                # Check if files array exists
                files_count = len(result.get("files", []))
                logger.info(f"{Fore.GREEN}✓ Found {files_count} files in the response{Style.RESET_ALL}")
                
                # Display file details if any
                for i, file in enumerate(result.get("files", [])):
                    logger.info(f"{Fore.GREEN}File {i+1}:{Style.RESET_ALL}")
                    logger.info(f"  File ID: {file.get('file_id', '')}")
                    logger.info(f"  File Name: {file.get('file_name', '')}")
                    logger.info(f"  File Type: {file.get('file_type', '')}")
                    logger.info(f"  Tags: {file.get('tags', [])}")
                    logger.info(f"  Relevance Score: {file.get('relevance_score', 0.0)}")
            else:
                logger.info(f"{Fore.RED}✗ Response does not contain the expected fields{Style.RESET_ALL}")
        else:
            logger.info(f"{Fore.RED}✗ Request failed with status code {response.status_code}{Style.RESET_ALL}")
            logger.info(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
    
    except Exception as e:
        logger.info(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
    
    logger.info(f"{Fore.YELLOW}----------------------------------------{Style.RESET_ALL}")
    logger.info("")

def main():
    """Main function to run the tests."""
    logger.info(f"{Fore.YELLOW}Testing /api/v1/rag/vector-search-tenant-docs API endpoint...{Style.RESET_ALL}")
    logger.info("")
    
    # Payload 1: Search for financial documents
    payload1 = {
        "query": "financial performance report for 2023",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "pdf",
            "tags": ["financial", "2023"]
        },
        "limit": 5
    }
    
    # Payload 2: Search for marketing strategy documents
    payload2 = {
        "query": "marketing strategy and target demographics",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "docx",
            "tags": ["marketing", "strategy"]
        },
        "limit": 5
    }
    
    # Payload 3: Search for product roadmap
    payload3 = {
        "query": "product roadmap and AI-powered analytics platform",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "file_type": "pptx",
            "tags": ["product", "roadmap"]
        },
        "limit": 5
    }
    
    # Payload 4: Search using general 2023 documents
    payload4 = {
        "query": "all reports and documents for 2023",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {
            "tags": ["2023"]
        },
        "limit": 5
    }
    
    # Payload 5: Search across all document types
    payload5 = {
        "query": "business strategy and performance insights",
        "organization_id": "test_org_123",
        "tenant_id": "default",
        "filters": {},
        "limit": 5
    }
    
    # Test each payload
    test_payload("1 (Financial Documents)", payload1)
    test_payload("2 (Marketing Strategy)", payload2)
    test_payload("3 (Product Roadmap)", payload3)
    test_payload("4 (2023 Documents)", payload4)
    test_payload("5 (All Document Types)", payload5)
    
    logger.info(f"{Fore.GREEN}Testing completed!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()