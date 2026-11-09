import asyncio
from src.data_stores.weaviate_client import WeaviateClient

async def list_all_tenant_files():
    """List all objects in the Tenant_UploadedFiles class"""
    print("\n=== Listing all objects in Tenant_UploadedFiles class ===")
    
    # Initialize Weaviate client
    weaviate_client = WeaviateClient('http://localhost:8080', None)
    
    try:
        # Get all objects in the Tenant_UploadedFiles class
        objects = weaviate_client.client.data_object.get(class_name="Tenant_UploadedFiles", with_vector=False)
        
        print(f"Found {len(objects)} objects in Tenant_UploadedFiles class")
        
        for i, obj in enumerate(objects):
            print(f"\nObject {i+1}:")
            print(f"  UUID: {obj.get('id', 'unknown')}")
            print(f"  Properties:")
            
            properties = obj.get("properties", {})
            for key, value in properties.items():
                if key == "content_chunk":
                    print(f"    {key}: {value[:100]}..." if value else f"    {key}: None")
                else:
                    print(f"    {key}: {value}")
    
    except Exception as e:
        print(f"Error listing objects: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_all_tenant_files())