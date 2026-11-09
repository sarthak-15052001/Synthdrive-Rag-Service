import asyncio
from src.data_stores.weaviate_client import WeaviateClient

async def test_direct_query():
    """Test direct query of Tenant_UploadedFiles class"""
    # Initialize Weaviate client
    weaviate_client = WeaviateClient('http://localhost:8080', None)
    
    # Test organization IDs
    org_id = "test-org-1"
    
    print(f"\n=== Testing direct query for organization {org_id} ===")
    
    try:
        # Build a direct query to the Tenant_UploadedFiles class
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
        result = query_builder.do()
        
        # Process the results
        print("Query result:", result)
        
        if result and "data" in result and "Get" in result["data"] and "Tenant_UploadedFiles" in result["data"]["Get"]:
            files = result["data"]["Get"]["Tenant_UploadedFiles"]
            print(f"Found {len(files)} files")
            
            for i, file in enumerate(files):
                print(f"\nFile {i+1}:")
                print(f"  File ID: {file.get('file_id', 'unknown')}")
                print(f"  File Name: {file.get('file_name', 'unknown')}")
                print(f"  Organization ID: {file.get('organization_id', 'unknown')}")
                print(f"  Content: {file.get('content_chunk', '')[:100]}...")
        else:
            print("No files found or unexpected result format")
    
    except Exception as e:
        print(f"Error in direct query: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_direct_query())