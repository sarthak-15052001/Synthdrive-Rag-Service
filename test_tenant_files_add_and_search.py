import asyncio
import traceback
from datetime import datetime
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.tenant_files_search import TenantUploadedFilesSearchTool

async def test_add_and_search():
    """Test adding a file and then searching for it"""
    print("\n=== Testing adding a file and then searching for it ===")
    
    try:
        # Initialize Weaviate client
        print("Initializing Weaviate client...")
        weaviate_client = WeaviateClient('http://localhost:8080', None)
        
        # Initialize tenant files search tool
        print("Initializing TenantUploadedFilesSearchTool...")
        tenant_files_tool = TenantUploadedFilesSearchTool(weaviate_client=weaviate_client)
        
        # Test data
        org_id = "test-org-1"
        tenant_id = "default"
        
        # Create test file data
        file_data = {
            "file_name": "financial_report_2023.pdf",
            "file_path": f"gs://tenant-files/{org_id}/financial_report_2023.pdf",
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
            "organization_id": org_id,
            "upload_date": datetime.now().isoformat(),
            "file_type": ".pdf",
            "tags": ["financial", "report", "2023"],
            "tenant_id": tenant_id
        }
        
        print(f"Adding test file for organization {org_id}...")
        
        try:
            # Add the file to Weaviate
            file_id = weaviate_client.add_tenant_uploaded_file(
                file_data=file_data,
                organization_id=org_id,
                tenant_id=tenant_id
            )
            
            print(f"Successfully added file with ID: {file_id}")
            
            # Wait a moment for indexing
            print("Waiting 2 seconds for indexing...")
            await asyncio.sleep(2)
            
            print(f"\n=== Testing direct Weaviate query for organization {org_id} ===")
            
            # Build a direct query to the Tenant_UploadedFiles class
            print("Building direct query...")
            query_builder = (
                weaviate_client.client.query
                .get("Tenant_UploadedFiles", [
                    "file_id", "file_name", "file_path", "content_chunk", 
                    "organization_id", "upload_date", "file_type", "tags", "tenant_id"
                ])
                .with_where({
                    "path": ["organization_id"],
                    "operator": "Equal",
                    "valueString": org_id
                })
                .with_limit(10)
            )
            
            # Execute the query
            print("Executing direct query...")
            result = query_builder.do()
            
            # Process the results
            print("Direct query result:", result)
            
            if result and "data" in result and "Get" in result["data"] and "Tenant_UploadedFiles" in result["data"]["Get"]:
                files = result["data"]["Get"]["Tenant_UploadedFiles"]
                print(f"Found {len(files)} files directly")
                
                for i, file in enumerate(files):
                    print(f"\nFile {i+1}:")
                    print(f"  File ID: {file.get('file_id', 'unknown')}")
                    print(f"  File Name: {file.get('file_name', 'unknown')}")
                    print(f"  Organization ID: {file.get('organization_id', 'unknown')}")
                    print(f"  Content: {file.get('content_chunk', '')[:100]}...")
            else:
                print("No files found or unexpected result format in direct query")
            
            print(f"\n=== Testing search_tenant_uploaded_files method for organization {org_id} ===")
            
            # Test the search_tenant_uploaded_files method directly
            print("Calling search_tenant_uploaded_files method...")
            results = weaviate_client.search_tenant_uploaded_files(
                query="financial data strategic initiatives",
                organization_id=org_id,
                filters={"tenant_id": tenant_id},
                limit=10
            )
            
            print(f"Found {len(results)} results using search_tenant_uploaded_files method")
            
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  File ID: {result.get('file_id', 'unknown')}")
                print(f"  File Name: {result.get('file_name', 'unknown')}")
                print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
                print(f"  Content: {result.get('content_chunk', '')[:100]}...")
            
            print(f"\n=== Testing search_tenant_files method for organization {org_id} ===")
            
            # Test the search_tenant_files method
            print("Calling search_tenant_files method...")
            response = await tenant_files_tool.search_tenant_files(
                query="financial data strategic initiatives",
                organization_id=org_id,
                tenant_id=tenant_id,
                filters={},
                limit=10
            )
            
            results = response.get("results", [])
            print(f"Found {len(results)} results using search_tenant_files method")
            
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  File ID: {result.get('file_id', 'unknown')}")
                print(f"  File Name: {result.get('file_name', 'unknown')}")
                print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
                print(f"  Content: {result.get('content_chunk', '')[:100]}...")
            
            # Test with prompt generation
            print(f"\n=== Testing search_and_generate_prompt method for organization {org_id} ===")
            
            # Test the search_and_generate_prompt method
            print("Calling search_and_generate_prompt method...")
            response = await tenant_files_tool.search_and_generate_prompt(
                query="financial data strategic initiatives",
                organization_id=org_id,
                tenant_id=tenant_id,
                filters={},
                limit=10
            )
            
            results = response.get("results", [])
            prompt = response.get("prompt", "")
            
            print(f"Found {len(results)} results with prompt generation")
            print(f"Prompt length: {len(prompt)} characters")
            print("Prompt preview:")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            
        except Exception as e:
            print(f"Error in file operations: {str(e)}")
            traceback.print_exc()
    
    except Exception as e:
        print(f"Error in test: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_add_and_search())