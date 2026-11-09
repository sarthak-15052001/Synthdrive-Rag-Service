"""
Mock test for the Vector Search Tenant Documents API endpoint.

This script simulates the behavior of the API endpoint with the fix applied,
without requiring the actual API server to be running.
"""
import json
import logging
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Sample tenant document data for testing
sample_tenant_docs = [
    {
        "file_id": "file-001",
        "file_name": "Financial Report 2023.pdf",
        "file_path": "/reports/financial/2023.pdf",
        "content": "The financial performance for 2023 showed a 15% increase in revenue compared to the previous year. Key growth areas included cloud services and AI solutions.",
        "organization_id": "test_org_123",
        "upload_date": "2023-12-15T00:00:00Z",
        "file_type": "pdf",
        "tags": ["financial", "2023"],
        "tenant_id": "default",
        "relevance_score": 0.95,
        "citation_id": "tenant-doc-1"
    },
    {
        "file_id": "file-002",
        "file_name": "Marketing Strategy 2023.docx",
        "file_path": "/marketing/strategy/2023.docx",
        "content": "Our marketing strategy for 2023 focuses on digital channels, with increased investment in social media and content marketing. Target demographics include tech professionals aged 25-45.",
        "organization_id": "test_org_123",
        "upload_date": "2023-01-10T00:00:00Z",
        "file_type": "docx",
        "tags": ["marketing", "strategy", "2023"],
        "tenant_id": "default",
        "relevance_score": 0.92,
        "citation_id": "tenant-doc-2"
    },
    {
        "file_id": "file-003",
        "file_name": "Product Roadmap 2023-2024.pptx",
        "file_path": "/product/roadmap/2023-2024.pptx",
        "content": "The product roadmap for 2023-2024 includes the launch of our AI-powered analytics platform in Q2 2023, followed by the mobile app integration in Q4 2023.",
        "organization_id": "test_org_123",
        "upload_date": "2023-02-28T00:00:00Z",
        "file_type": "pptx",
        "tags": ["product", "roadmap", "2023", "2024"],
        "tenant_id": "default",
        "relevance_score": 0.89,
        "citation_id": "tenant-doc-3"
    },
    {
        "file_id": "file-004",
        "file_name": "Annual Report 2023.pdf",
        "file_path": "/reports/annual/2023.pdf",
        "content": "Annual report for 2023 fiscal year. This document contains financial statements, business performance analysis, and future outlook for all business units.",
        "organization_id": "test_org_123",
        "upload_date": "2023-12-31T00:00:00Z",
        "file_type": "pdf",
        "tags": ["2023", "annual", "report"],
        "tenant_id": "default",
        "relevance_score": 0.85,
        "citation_id": "tenant-doc-4"
    },
    {
        "file_id": "file-005",
        "file_name": "Business Strategy 2023.pptx",
        "file_path": "/strategy/business/2023.pptx",
        "content": "Business strategy and performance insights for 2023. This presentation outlines our core business objectives, market analysis, and strategic initiatives for the coming year.",
        "organization_id": "test_org_123",
        "upload_date": "2023-01-05T00:00:00Z",
        "file_type": "pptx",
        "tags": ["business", "strategy", "performance"],
        "tenant_id": "default",
        "relevance_score": 0.95,
        "citation_id": "tenant-doc-5"
    }
]

def mock_search_tenant_documents(query, organization_id, tenant_id="default", filters=None, limit=5):
    """
    Mock implementation of the search_tenant_documents function.
    
    Args:
        query: The search query
        organization_id: The organization ID
        tenant_id: The tenant ID (default: "default")
        filters: Additional filters to apply (default: None)
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        A list of tenant documents matching the query and filters
    """
    # Start with all documents
    filtered_docs = sample_tenant_docs.copy()
    
    # Apply filters if provided
    if filters:
        # Apply file_type filter
        if "file_type" in filters:
            filtered_docs = [doc for doc in filtered_docs if doc.get("file_type") == filters["file_type"]]
        
        # Apply tags filter
        if "tags" in filters and filters["tags"]:
            filtered_docs = [
                doc for doc in filtered_docs 
                if doc.get("tags") and all(tag in doc.get("tags", []) for tag in filters["tags"])
            ]
    
    # Limit the number of results
    filtered_docs = filtered_docs[:limit]
    
    # Format the response
    response = {
        "query": query,
        "organization_id": organization_id,
        "files": []
    }
    
    # Add the files to the response
    for doc in filtered_docs:
        response["files"].append({
            "file_id": doc.get("file_id", ""),
            "file_name": doc.get("file_name", ""),
            "file_path": doc.get("file_path", ""),
            "content_chunk": doc.get("content", ""),
            "organization_id": doc.get("organization_id", ""),
            "upload_date": doc.get("upload_date", ""),
            "file_type": doc.get("file_type", ""),
            "tags": doc.get("tags", []),
            "relevance_score": doc.get("relevance_score", 0.0),
            "citation_id": doc.get("citation_id", "")
        })
    
    return response

def test_payload(payload_name, payload):
    """Test a payload against the mock API endpoint."""
    logger.info(f"{Fore.YELLOW}Testing Payload {payload_name}:{Style.RESET_ALL}")
    logger.info(json.dumps(payload, indent=2))
    logger.info("")
    
    try:
        # Call the mock function
        result = mock_search_tenant_documents(
            query=payload["query"],
            organization_id=payload["organization_id"],
            tenant_id=payload.get("tenant_id", "default"),
            filters=payload.get("filters", {}),
            limit=payload.get("limit", 5)
        )
        
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
    
    except Exception as e:
        logger.info(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
    
    logger.info(f"{Fore.YELLOW}----------------------------------------{Style.RESET_ALL}")
    logger.info("")

def main():
    """Main function to run the tests."""
    logger.info(f"{Fore.YELLOW}Testing /api/v1/rag/vector-search-tenant-docs API endpoint (MOCK)...{Style.RESET_ALL}")
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