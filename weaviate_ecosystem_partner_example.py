"""
Example script showing how to add an ecosystem partner to Weaviate's Global_Ecosystem collection
and then search for it using the Weaviate Python client directly.

This bypasses the API and works directly with Weaviate.
"""

import weaviate
from weaviate.auth import AuthApiKey
import uuid
import json
import time
import os
from datetime import datetime, timezone

# Weaviate connection settings - set these as environment variables or modify directly
WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Required for text2vec-openai vectorizer

def main():
    # Step 1: Connect to Weaviate
    client = connect_to_weaviate()
    
    # Step 2: Add a sample ecosystem partner
    partner_id = add_ecosystem_partner(client)
    
    # Step 3: Wait for indexing to complete
    print("\nWaiting for indexing to complete...")
    time.sleep(3)
    
    # Step 4: Search for the partner
    search_ecosystem_partners(client, "supply chain experts")

def connect_to_weaviate():
    """Connect to Weaviate instance"""
    print(f"Connecting to Weaviate at {WEAVIATE_URL}...")
    
    # For local instances
    if "localhost" in WEAVIATE_URL or "127.0.0.1" in WEAVIATE_URL:
        client = weaviate.Client(
            url=WEAVIATE_URL,
            additional_headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        )
    # For remote instances with authentication
    else:
        auth_config = AuthApiKey(api_key=WEAVIATE_API_KEY) if WEAVIATE_API_KEY else None
        client = weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        )
    
    # Test connection
    try:
        client.schema.get()
        print("Successfully connected to Weaviate")
        return client
    except Exception as e:
        print(f"Error connecting to Weaviate: {str(e)}")
        raise

def add_ecosystem_partner(client):
    """Add a sample ecosystem partner to the Global_Ecosystem collection"""
    # Generate a unique partner ID
    partner_id = str(uuid.uuid4())
    
    # Create the partner data object
    partner_data = {
        "name": "SupplyChain Solutions Inc.",
        "bio": "SupplyChain Solutions Inc. is a leading consulting firm specializing in end-to-end supply chain optimization. With over 15 years of experience, we help companies streamline their logistics, reduce costs, and improve operational efficiency.",
        "expertise": [
            "Supply Chain Optimization",
            "Logistics Management",
            "Inventory Control",
            "Demand Forecasting"
        ],
        "certifications": [
            "APICS Certified Supply Chain Professional",
            "Six Sigma Black Belt",
            "ISM Certified Professional in Supply Management"
        ],
        "case_studies": "Helped a Fortune 500 retailer reduce inventory costs by 23% while improving order fulfillment rates by implementing advanced forecasting algorithms and warehouse optimization techniques.",
        "website": "https://supplychainsolutions.example.com",
        "contact_info": "contact@supplychainsolutions.example.com | +1-555-123-4567",
        "budget_tier": "enterprise",
        "partner_id": partner_id,
        "tags": [
            "supply chain",
            "logistics",
            "consulting",
            "enterprise"
        ],
        "tenant_id": "default"
    }
    
    # Create combined content for better embedding
    # This is important for semantic search to work well
    content = f"Partner name: {partner_data.get('name', '')}\n"
    content += f"Bio: {partner_data.get('bio', '')}\n"
    content += f"Expertise: {', '.join(partner_data.get('expertise', []))}\n"
    content += f"Case studies: {partner_data.get('case_studies', '')}\n"
    
    # Add content to partner_data
    partner_data["content"] = content
    
    # Check if Global_Ecosystem class exists
    schema = client.schema.get()
    classes = [cls.get("class") for cls in schema.get("classes", [])]
    
    if "Global_Ecosystem" not in classes:
        print("Global_Ecosystem class doesn't exist. Creating it...")
        create_global_ecosystem_class(client)
    
    # Add the partner to Weaviate
    print(f"Adding ecosystem partner with ID: {partner_id}")
    try:
        # The data_object.create method will automatically vectorize the object
        # using the configured vectorizer (text2vec-openai)
        obj_uuid = client.data_object.create(
            class_name="Global_Ecosystem",
            data_object=partner_data
        )
        print(f"Successfully added partner with UUID: {obj_uuid}")
        
        # Verify the object was created
        result = client.data_object.get(class_name="Global_Ecosystem", uuid=obj_uuid)
        print(f"Verified partner was added: {result.get('name', 'Unknown')}")
        
        return partner_id
    except Exception as e:
        print(f"Error adding ecosystem partner: {str(e)}")
        raise

def create_global_ecosystem_class(client):
    """Create the Global_Ecosystem class in Weaviate"""
    class_obj = {
        "class": "Global_Ecosystem",
        "vectorizer": "text2vec-openai",  # Using OpenAI's embedding model
        "moduleConfig": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        },
        "properties": [
            {
                "name": "name",
                "dataType": ["string"],
                "description": "Name of the ecosystem partner"
            },
            {
                "name": "bio",
                "dataType": ["text"],
                "description": "Biography or description of the partner"
            },
            {
                "name": "expertise",
                "dataType": ["string[]"],
                "description": "Areas of expertise"
            },
            {
                "name": "certifications",
                "dataType": ["string[]"],
                "description": "Certifications held by the partner"
            },
            {
                "name": "case_studies",
                "dataType": ["text"],
                "description": "Case studies or success stories"
            },
            {
                "name": "website",
                "dataType": ["string"],
                "description": "Partner's website"
            },
            {
                "name": "contact_info",
                "dataType": ["string"],
                "description": "Contact information"
            },
            {
                "name": "budget_tier",
                "dataType": ["string"],
                "description": "Budget tier (enterprise, mid-market, etc.)"
            },
            {
                "name": "partner_id",
                "dataType": ["string"],
                "description": "Unique identifier for the partner"
            },
            {
                "name": "tags",
                "dataType": ["string[]"],
                "description": "Tags associated with the partner"
            },
            {
                "name": "content",
                "dataType": ["text"],
                "description": "Combined content for embedding"
            },
            {
                "name": "tenant_id",
                "dataType": ["string"],
                "description": "Tenant ID"
            }
        ]
    }
    
    client.schema.create_class(class_obj)
    print("Created Global_Ecosystem class in Weaviate")

def search_ecosystem_partners(client, query):
    """Search for ecosystem partners using semantic search"""
    print(f"\nSearching for ecosystem partners with query: '{query}'")
    
    # Expand the query for better semantic search
    # This is the same technique used in the API implementation
    expanded_query = f"Expert in {query}"
    
    # Define properties to retrieve
    properties = [
        "name", "bio", "expertise", "certifications", "case_studies",
        "website", "contact_info", "budget_tier", "partner_id",
        "tags", "content", "tenant_id"
    ]
    
    # Build and execute the query
    try:
        # The with_near_text method performs semantic search using the text2vec-openai vectorizer
        query_result = (
            client.query
            .get("Global_Ecosystem", properties)
            .with_near_text({"concepts": [expanded_query]})
            .with_limit(5)
            .with_additional(["id", "certainty"])  # certainty is the relevance score
            .do()
        )
        
        # Process and display results
        results = query_result.get("data", {}).get("Get", {}).get("Global_Ecosystem", [])
        
        print(f"\nFound {len(results)} ecosystem partners matching the query.")
        
        # Format results like the API response
        api_response = {
            "query": query,
            "partners": []
        }
        
        for i, result in enumerate(results):
            partner = {
                "partner_id": result.get("partner_id", f"partner-{i+1}"),
                "name": result.get("name", "Unknown Partner"),
                "bio": result.get("bio", ""),
                "expertise": result.get("expertise", []),
                "certifications": result.get("certifications", []),
                "case_studies": result.get("case_studies", ""),
                "website": result.get("website", ""),
                "contact_info": result.get("contact_info", ""),
                "budget_tier": result.get("budget_tier", ""),
                "tags": result.get("tags", []),
                "relevance_score": result["_additional"]["certainty"],
                "citation_id": f"partner-{i+1}"
            }
            
            api_response["partners"].append(partner)
            
            # Print summary of each partner
            print(f"\nPartner {i+1}: {partner['name']}")
            print(f"Expertise: {', '.join(partner['expertise'])}")
            print(f"Relevance Score: {partner['relevance_score']}")
        
        # Save the response to a file
        with open("ecosystem_partners_search_result.json", "w") as f:
            json.dump(api_response, f, indent=2)
        
        print("\nSaved search results to ecosystem_partners_search_result.json")
        
        return api_response
    except Exception as e:
        print(f"Error searching for ecosystem partners: {str(e)}")
        return {"query": query, "partners": []}

if __name__ == "__main__":
    main()