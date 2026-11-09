import asyncio
from src.data_stores.weaviate_client import WeaviateClient
from src.querying.tools.tenant_files_search import TenantUploadedFilesSearchTool

async def test_search():
    # Initialize Weaviate client
    weaviate_client = WeaviateClient('http://localhost:8080', None)
    
    # Initialize tenant files search tool
    tenant_files_tool = TenantUploadedFilesSearchTool(weaviate_client=weaviate_client)
    
    # Test organization IDs
    org_ids = ["test-org-1", "test-org"]
    
    for org_id in org_ids:
        print(f"\n=== Testing search for organization {org_id} ===")
        
        # Search for files
        response = await tenant_files_tool.search_tenant_files(
            query="financial data strategic initiatives",
            organization_id=org_id,
            tenant_id="default",
            filters={},
            limit=10
        )
        
        # Print results
        results = response.get("results", [])
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  File ID: {result.get('file_id', 'unknown')}")
            print(f"  File Name: {result.get('file_name', 'unknown')}")
            print(f"  Organization ID: {result.get('organization_id', 'unknown')}")
            print(f"  Content: {result.get('content_chunk', '')[:100]}...")
            print(f"  Relevance: {result.get('relevance_score', 0)}")

if __name__ == "__main__":
    asyncio.run(test_search())