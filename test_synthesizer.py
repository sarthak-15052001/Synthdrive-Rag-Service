import asyncio
import json
import requests
from pprint import pprint

# Server URL
BASE_URL = "http://localhost:8000"

async def test_synthesizer():
    """
    Test the Synthesizer endpoint with a sample query and data.
    """
    print("Testing Synthesizer endpoint...")
    
    # Sample retrieved documents
    retrieved_docs = [
        {
            "content": "Runway is an AI video generation tool that allows users to create videos from text prompts. It offers features like text-to-video, image-to-video, and video editing capabilities.",
            "metadata": {"type": "ai_tool"},
            "source": "global_tools_database",
            "citation_id": "doc-1"
        },
        {
            "content": "Synthesia is a platform that enables users to create AI-generated videos with virtual presenters. Users can input text, and the platform will generate a video with a virtual human presenting the content.",
            "metadata": {"type": "ai_tool"},
            "source": "global_tools_database",
            "citation_id": "doc-2"
        }
    ]
    
    # Sample graph insights
    graph_insights = [
        {
            "content": "The marketing team has been using Runway for their recent video campaigns.",
            "metadata": {"type": "graph_relationship"},
            "source": "graph_database",
            "citation_id": "graph-rel-1",
            "explanation": "This insight shows that the marketing team has practical experience with Runway.",
            "inferred_context": "The marketing team might have valuable feedback on Runway's effectiveness for promotional content."
        }
    ]
    
    # Create the request payload
    payload = {
        "query": "What AI tools are available for video generation?",
        "organization_id": "test-org-123",
        "tenant_id": "default",
        "retrieved_docs": retrieved_docs,
        "graph_insights": graph_insights
    }
    
    # Send the request to the Synthesizer endpoint
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/rag/synthesizer",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("\nSynthesizer Response:")
            print(f"Query: {result.get('query')}")
            print(f"Organization ID: {result.get('organization_id')}")
            print("\nFinal Answer:")
            print(result.get('final_answer'))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_synthesizer())