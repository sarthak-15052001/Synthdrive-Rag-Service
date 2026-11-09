import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8001/api/v1"

def test_ai_tools_search():
    """
    Test the AI tools search endpoint.
    """
    # Define the search query
    search_query = {
        "query": "find a tool to make videos from text",
        "tenant_id": "default",
        "limit": 5
    }
    
    # Make the request to the AI tools search endpoint
    response = requests.post(
        f"{BASE_URL}/tools/search",
        json=search_query
    )
    
    # Print the status code
    print(f"Status code: {response.status_code}")
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response
        result = response.json()
        
        # Print the query
        print(f"\nQuery: {result.get('query')}")
        
        # Print the tools
        print("\nTools found:")
        for i, tool in enumerate(result.get('tools', []), 1):
            print(f"\n{i}. {tool.get('name')}")
            print(f"   Description: {tool.get('description')}")
            print(f"   URL: {tool.get('url')}")
            print(f"   Category: {tool.get('category', 'N/A')}")
            print(f"   Pricing: {tool.get('pricing', 'N/A')}")
            print(f"   Rating: {tool.get('rating', 'N/A')}")
            print(f"   Relevance Score: {tool.get('relevance_score', 'N/A')}")
    else:
        # Print the error message
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_ai_tools_search()