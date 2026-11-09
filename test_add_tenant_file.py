import asyncio
from datetime import datetime
from src.data_stores.weaviate_client import WeaviateClient

async def add_test_document():
    # Initialize Weaviate client
    weaviate_client = WeaviateClient('http://localhost:8080', None)
    
    # Test data
    org_id = "test-org-1"
    tenant_id = "default"
    
    # Create test file data
    file_data = {
        "file_name": "test_corporate_intelligence.txt",
        "file_path": f"gs://tenant-files/{org_id}/test_corporate_intelligence.txt",
        "content_chunk": """
        CORPORATE INTELLIGENCE REPORT
        Organization: test-org-1
        Date: 2023-10-23
        
        EXECUTIVE SUMMARY
        This document contains confidential corporate intelligence for test-org-1.
        The information includes financial data, strategic initiatives, and market analysis.
        
        FINANCIAL PERFORMANCE
        Revenue: $125M (Q3 2023)
        Growth: 15% YoY
        EBITDA Margin: 28%
        
        STRATEGIC INITIATIVES
        1. Expansion into APAC region by Q2 2024
        2. Launch of new product line "Quantum Series"
        3. Digital transformation of supply chain operations
        
        MARKET ANALYSIS
        - Current market share: 23%
        - Main competitors: CompA (31%), CompB (18%), CompC (12%)
        - Growth opportunities in healthcare and financial services verticals
        
        CONFIDENTIAL - FOR INTERNAL USE ONLY
        """,
        "organization_id": org_id,
        "upload_date": datetime.now().isoformat(),
        "file_type": ".txt",
        "tags": ["corporate", "intelligence", "financial"],
        "tenant_id": tenant_id
    }
    
    print(f"Adding test document for organization {org_id}...")
    
    try:
        # Add the document to Weaviate
        file_id = weaviate_client.add_tenant_uploaded_file(
            file_data=file_data,
            organization_id=org_id,
            tenant_id=tenant_id
        )
        
        print(f"Successfully added document with ID: {file_id}")
        return file_id
    except Exception as e:
        print(f"Error adding document: {str(e)}")
        return None

if __name__ == "__main__":
    file_id = asyncio.run(add_test_document())
    print(f"Test document ID: {file_id}")