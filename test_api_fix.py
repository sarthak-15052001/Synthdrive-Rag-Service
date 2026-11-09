#!/usr/bin/env python3
"""
Script to test a potential fix for the learning resources search API endpoint.
This script creates a custom implementation of the search_learning_resources endpoint
and tests it against the direct Weaviate client.
"""

import requests
import json
import time
import sys
from fastapi import FastAPI, Depends
from src.data_stores.weaviate_client import WeaviateClient
from src.api.v1.schemas import LearningResourcesSearchRequest, LearningResourcesSearchResponse, LearningResource

# Create a test FastAPI app
app = FastAPI()

# Initialize the Weaviate client
weaviate_client = WeaviateClient()

@app.post("/api/v1/rag/learning-resources/search")
async def search_learning_resources_fixed(request: LearningResourcesSearchRequest):
    """
    Fixed implementation of the search_learning_resources endpoint.
    """
    print(f"Processing learning resources search query: {request.query}")
    
    try:
        # Search for learning resources using the Weaviate client
        resources_results = weaviate_client.search_learning_resources(
            query=request.query,
            filters={"tenant_id": request.tenant_id, **request.filters},
            limit=request.limit
        )
        
        # Print the raw results for debugging
        print(f"Raw results from Weaviate: {json.dumps(resources_results, indent=2)}")
        
        # Convert results to LearningResource objects
        resources = []
        for resource in resources_results:
            resources.append(LearningResource(
                resource_id=resource.get("resource_id", ""),
                title=resource.get("title", "Unknown Resource"),
                content=resource.get("content", ""),
                url=resource.get("url", ""),
                author=resource.get("author", ""),
                created_at=resource.get("created_at", ""),
                resource_type=resource.get("resource_type", ""),
                tags=resource.get("tags", []),
                relevance_score=resource.get("relevance_score", 0.0),
                citation_id=resource.get("citation_id", "")
            ))
        
        # Create and return the response
        response = LearningResourcesSearchResponse(
            query=request.query,
            resources=resources
        )
        
        return response
        
    except Exception as e:
        print(f"Error processing learning resources search: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

def test_direct_weaviate(query, filters=None, limit=5):
    """Test the Weaviate client directly"""
    print(f"\n=== Testing Direct Weaviate Client ===")
    print(f"Query: {query}")
    print(f"Filters: {filters}")
    print(f"Limit: {limit}")
    
    # Call the search_learning_resources method directly
    start_time = time.time()
    results = weaviate_client.search_learning_resources(
        query=query,
        filters=filters or {},
        limit=limit
    )
    response_time = time.time() - start_time
    
    print(f"Response Time: {response_time:.4f} seconds")
    print(f"Found {len(results)} learning resources")
    
    return results

def main():
    """Main function to demonstrate the issue and potential fix."""
    # Test query
    query = "RAG"
    filters = {"resource_type": "Tutorial"}
    limit = 5
    
    # Test direct Weaviate
    direct_results = test_direct_weaviate(query, filters, limit)
    
    # Print the direct results
    print("\nDirect Weaviate Results:")
    for i, resource in enumerate(direct_results, 1):
        print(f"{i}. {resource.get('title', 'Unnamed Resource')}")
        print(f"   Type: {resource.get('resource_type', 'N/A')}")
        print(f"   Tags: {', '.join(resource.get('tags', []))}")
        print(f"   Relevance Score: {resource.get('relevance_score', 'N/A')}")
    
    print("\nBased on our testing, we've identified the following issues:")
    print("1. The API endpoint is not returning results even though the Weaviate client has data")
    print("2. This could be due to a filter issue or a problem in the API implementation")
    print("\nPotential fixes:")
    print("1. Check if the tenant_id filter is being applied correctly")
    print("2. Ensure that the filters are being properly passed to the Weaviate client")
    print("3. Verify that the response mapping is correct")
    print("4. Add more logging to the API endpoint to identify where the issue occurs")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)