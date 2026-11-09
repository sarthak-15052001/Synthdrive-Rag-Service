import asyncio
import traceback
from datetime import datetime, timezone
import uuid
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.tenant_files_search import TenantUploadedFilesSearchTool

async def test_tenant_files_comprehensive():
    """
    Comprehensive test for tenant uploaded files functionality.
    
    This test covers:
    1. Adding files for multiple organizations
    2. Searching for files with organization isolation
    3. Testing prompt generation with proper citations
    4. Cross-organization search to verify isolation
    """
    print("\n=== COMPREHENSIVE TEST FOR TENANT UPLOADED FILES ===")
    
    try:
        # Initialize Weaviate client
        print("Initializing Weaviate client...")
        weaviate_client = WeaviateClient('http://localhost:8080', None)
        
        # Initialize tenant files search tool
        print("Initializing TenantUploadedFilesSearchTool...")
        tenant_files_tool = TenantUploadedFilesSearchTool(weaviate_client=weaviate_client)
        
        # Test data for multiple organizations
        org_1_id = "test-org-1"
        org_2_id = "test-org-2"
        tenant_id = "default"
        
        # Create test file data for organization 1
        org_1_file_data = {
            "file_name": "financial_report_2023.pdf",
            "file_path": f"gs://tenant-files/{org_1_id}/financial_report_2023.pdf",
            "content_chunk": """
            FINANCIAL REPORT 2023
            Organization: test-org-1
            
            EXECUTIVE SUMMARY
            This document contains financial data for test-org-1 for the fiscal year 2023.
            
            FINANCIAL PERFORMANCE
            Revenue: $125M (Q3 2023)
            Growth: 15% YoY
            EBITDA Margin: 28%
            
            STRATEGIC INITIATIVES
            1. Expansion into APAC region by Q2 2024
            2. Launch of new product line "Quantum Series"
            3. Digital transformation of supply chain operations
            
            CONFIDENTIAL - FOR INTERNAL USE ONLY
            """,
            "organization_id": org_1_id,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "file_type": ".pdf",
            "tags": ["financial", "report", "2023"],
            "tenant_id": tenant_id
        }
        
        # Create test file data for organization 2
        org_2_file_data = {
            "file_name": "product_roadmap.pdf",
            "file_path": f"gs://tenant-files/{org_2_id}/product_roadmap.pdf",
            "content_chunk": """
            PRODUCT ROADMAP 2024
            Organization: test-org-2
            
            EXECUTIVE SUMMARY
            This document outlines the product strategy for test-org-2 for the year 2024.
            
            PRODUCT INITIATIVES
            1. Cloud-native platform migration (Q1 2024)
            2. AI-powered analytics dashboard (Q2 2024)
            3. Mobile application redesign (Q3 2024)
            
            MARKET ANALYSIS
            Target market: Enterprise customers
            Competitive positioning: Premium features with competitive pricing
            Growth forecast: 25% user base expansion
            
            CONFIDENTIAL - FOR INTERNAL USE ONLY
            """,
            "organization_id": org_2_id,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "file_type": ".pdf",
            "tags": ["product", "roadmap", "strategy"],
            "tenant_id": tenant_id
        }
        
        # STEP 1: Add files for both organizations
        print(f"\n=== STEP 1: Adding files for multiple organizations ===")
        
        # Add file for organization 1
        print(f"Adding test file for organization {org_1_id}...")
        org_1_file_id = weaviate_client.add_tenant_uploaded_file(
            file_data=org_1_file_data,
            organization_id=org_1_id,
            tenant_id=tenant_id
        )
        print(f"Successfully added file for org 1 with ID: {org_1_file_id}")
        
        # Add file for organization 2
        print(f"Adding test file for organization {org_2_id}...")
        org_2_file_id = weaviate_client.add_tenant_uploaded_file(
            file_data=org_2_file_data,
            organization_id=org_2_id,
            tenant_id=tenant_id
        )
        print(f"Successfully added file for org 2 with ID: {org_2_file_id}")
        
        # Wait for indexing
        print("Waiting 2 seconds for indexing...")
        await asyncio.sleep(2)
        
        # STEP 2: Search for organization 1's files
        print(f"\n=== STEP 2: Searching for organization {org_1_id}'s files ===")
        
        org_1_response = await tenant_files_tool.search_tenant_files(
            query="financial data strategic initiatives",
            organization_id=org_1_id,
            tenant_id=tenant_id,
            filters={},
            limit=10
        )
        
        org_1_results = org_1_response.get("results", [])
        print(f"Found {len(org_1_results)} results for organization {org_1_id}")
        
        for i, result in enumerate(org_1_results):
            print(f"\nResult {i+1}:")
            print(f"  File ID: {result.get('file_id', 'unknown')}")
            print(f"  File Name: {result.get('file_name', 'unknown')}")
            print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
            print(f"  Content: {result.get('content_chunk', '')[:100]}...")
        
        # STEP 3: Search for organization 2's files
        print(f"\n=== STEP 3: Searching for organization {org_2_id}'s files ===")
        
        org_2_response = await tenant_files_tool.search_tenant_files(
            query="product roadmap initiatives",
            organization_id=org_2_id,
            tenant_id=tenant_id,
            filters={},
            limit=10
        )
        
        org_2_results = org_2_response.get("results", [])
        print(f"Found {len(org_2_results)} results for organization {org_2_id}")
        
        for i, result in enumerate(org_2_results):
            print(f"\nResult {i+1}:")
            print(f"  File ID: {result.get('file_id', 'unknown')}")
            print(f"  File Name: {result.get('file_name', 'unknown')}")
            print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
            print(f"  Content: {result.get('content_chunk', '')[:100]}...")
        
        # STEP 4: Cross-organization search to verify isolation
        print(f"\n=== STEP 4: Cross-organization search to verify isolation ===")
        
        # Search for org 2 content using org 1's ID (should not return org 2's content)
        print(f"Searching for org 2 content using org 1's ID...")
        cross_org_response = await tenant_files_tool.search_tenant_files(
            query="product roadmap mobile application",  # Terms from org 2's document
            organization_id=org_1_id,  # But using org 1's ID
            tenant_id=tenant_id,
            filters={},
            limit=10
        )
        
        cross_org_results = cross_org_response.get("results", [])
        print(f"Found {len(cross_org_results)} results when searching for org 2 content using org 1's ID")
        
        # Check if any results contain org 2's ID (should be none)
        org_2_content_found = False
        for result in cross_org_results:
            if result.get("organization_id") == org_2_id:
                org_2_content_found = True
                print(f"WARNING: Found org 2 content when searching with org 1's ID!")
                break
        
        if not org_2_content_found:
            print("SUCCESS: Organization isolation is working correctly - no cross-organization data leakage")
        
        # STEP 5: Test prompt generation
        print(f"\n=== STEP 5: Testing prompt generation ===")
        
        # Generate prompt for organization 1
        print(f"Generating prompt for organization {org_1_id}...")
        prompt_response = await tenant_files_tool.search_and_generate_prompt(
            query="What are the strategic initiatives for 2024?",
            organization_id=org_1_id,
            tenant_id=tenant_id,
            filters={},
            limit=5
        )
        
        prompt = prompt_response.get("prompt", "")
        print(f"Generated prompt length: {len(prompt)} characters")
        print("Prompt preview:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
        # Check if the prompt contains organization ID for security context
        if org_1_id in prompt:
            print(f"SUCCESS: Prompt contains organization ID ({org_1_id}) for security context")
        else:
            print(f"WARNING: Prompt does not contain organization ID for security context")
        
        # Check if the prompt contains citation information
        if "financial_report_2023.pdf" in prompt:
            print(f"SUCCESS: Prompt contains file citation information")
        else:
            print(f"WARNING: Prompt does not contain file citation information")
        
        print("\n=== COMPREHENSIVE TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"Error in comprehensive test: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tenant_files_comprehensive())