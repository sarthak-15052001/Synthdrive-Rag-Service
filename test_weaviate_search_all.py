import weaviate
import os
from dotenv import load_dotenv
import json

def search_all_data():
    # Load environment variables
    load_dotenv()
    
    # Initialize Weaviate client
    client = weaviate.Client(
        url=os.getenv("WEAVIATE_URL"),
        auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
    )
    
    print("\n=== Checking Documents in Weaviate ===")
    
    # Query all documents with specific properties
    result = (
        client.query
        .get("Document", ["content", "metadata", "source", "tenant_id"])
        .with_additional(['id'])
        .do()
    )
    
    if result and 'data' in result and 'Get' in result['data'] and 'Document' in result['data']['Get']:
        documents = result['data']['Get']['Document']
        print(f"\nFound {len(documents)} documents:")
        
        for doc in documents:
            print("\nDocument Details:")
            print(f"Content: {doc.get('content', 'N/A')[:200]}...")
            
            # Parse metadata if it's a string
            metadata = doc.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            print("\nMetadata:")
            print(f"Source: {metadata.get('source', 'N/A')}")
            print(f"Author: {metadata.get('author', 'N/A')}")
            print(f"Document Type: {metadata.get('document_type', 'N/A')}")
            print(f"Tags: {metadata.get('tags', [])}")
            
            print(f"\nTenant ID: {doc.get('tenant_id', 'N/A')}")
            if '_additional' in doc:
                print(f"Document ID: {doc['_additional'].get('id', 'N/A')}")
            print("-" * 80)
    else:
        print("No documents found")

if __name__ == "__main__":
    search_all_data()