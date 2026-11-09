import asyncio
import json
from src.data_stores.weaviate_client import WeaviateClient

async def list_all_tenant_files():
    """List all objects in the Tenant_UploadedFiles class"""
    print("\n=== Listing all objects in Tenant_UploadedFiles class ===")
    
    # Initialize Weaviate client
    weaviate_client = WeaviateClient('http://localhost:8080', None)
    
    try:
        # Get all objects in the Tenant_UploadedFiles class using the query API
        query_result = weaviate_client.client.query.get(
            "Tenant_UploadedFiles", 
            ["file_id", "file_name", "file_path", "content_chunk", "organization_id", "upload_date", "file_type", "tags", "tenant_id"]
        ).do()
        
        print("Query result:", json.dumps(query_result, indent=2))
        
        if query_result and "data" in query_result and "Get" in query_result["data"] and "Tenant_UploadedFiles" in query_result["data"]["Get"]:
            objects = query_result["data"]["Get"]["Tenant_UploadedFiles"]
            print(f"Found {len(objects)} objects in Tenant_UploadedFiles class")
            
            for i, obj in enumerate(objects):
                print(f"\nObject {i+1}:")
                for key, value in obj.items():
                    if key == "content_chunk":
                        print(f"  {key}: {value[:100]}..." if value else f"  {key}: None")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("No objects found or unexpected result format")
    
    except Exception as e:
        print(f"Error listing objects: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_all_tenant_files())