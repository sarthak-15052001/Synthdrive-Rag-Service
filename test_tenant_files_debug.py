import asyncio
import traceback
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.tenant_files_search import TenantUploadedFilesSearchTool

async def test_search_debug():
    """Test search with detailed error handling"""
    print("\n=== Testing tenant files search with detailed error handling ===")
    
    try:
        # Initialize Weaviate client
        print("Initializing Weaviate client...")
        weaviate_client = WeaviateClient('http://localhost:8080', None)
        
        # Initialize tenant files search tool
        print("Initializing TenantUploadedFilesSearchTool...")
        tenant_files_tool = TenantUploadedFilesSearchTool(weaviate_client=weaviate_client)
        
        # Test organization ID
        org_id = "test-org-1"
        
        print(f"\n=== Testing direct Weaviate query for organization {org_id} ===")
        
        try:
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
        
        except Exception as e:
            print(f"Error in direct query: {str(e)}")
            traceback.print_exc()
        
        print(f"\n=== Testing search_tenant_uploaded_files method for organization {org_id} ===")
        
        try:
            # Test the search_tenant_uploaded_files method directly
            print("Calling search_tenant_uploaded_files method...")
            results = weaviate_client.search_tenant_uploaded_files(
                query="financial data strategic initiatives",
                organization_id=org_id,
                filters={"tenant_id": "default"},
                limit=10
            )
            
            print(f"Found {len(results)} results using search_tenant_uploaded_files method")
            
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  File ID: {result.get('file_id', 'unknown')}")
                print(f"  File Name: {result.get('file_name', 'unknown')}")
                print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
                print(f"  Content: {result.get('content_chunk', '')[:100]}...")
        
        except Exception as e:
            print(f"Error in search_tenant_uploaded_files: {str(e)}")
            traceback.print_exc()
        
        print(f"\n=== Testing search_tenant_files method for organization {org_id} ===")
        
        try:
            # Test the search_tenant_files method
            print("Calling search_tenant_files method...")
            response = await tenant_files_tool.search_tenant_files(
                query="financial data strategic initiatives",
                organization_id=org_id,
                tenant_id="default",
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
        
        except Exception as e:
            print(f"Error in search_tenant_files: {str(e)}")
            traceback.print_exc()
    
    except Exception as e:
        print(f"Error in test: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search_debug())