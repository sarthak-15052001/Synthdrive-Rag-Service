import weaviate
from weaviate.auth import AuthApiKey
import uuid
import json
import time
import os
from datetime import datetime, timezone

# Weaviate connection settings
WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.environ.get("WEAVIATE_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def create_weaviate_client():
    """Create and return a Weaviate client"""
    # Check if this is a local instance (no authentication needed)
    is_local = "localhost" in WEAVIATE_URL or "127.0.0.1" in WEAVIATE_URL
    
    if is_local:
        # For local instances with anonymous access enabled
        print(f"Connecting to local Weaviate instance at {WEAVIATE_URL}")
        return weaviate.Client(
            url=WEAVIATE_URL,
            additional_headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        )
    else:
        # For remote instances with API key authentication
        print(f"Connecting to remote Weaviate instance at {WEAVIATE_URL}")
        auth_config = AuthApiKey(api_key=WEAVIATE_API_KEY) if WEAVIATE_API_KEY else None
        
        return weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": OPENAI_API_KEY
            }
        )

def check_global_ecosystem_class(client):
    """Check if the Global_Ecosystem class exists, create it if not"""
    try:
        schema = client.schema.get()
        classes = [cls.get("class") for cls in schema.get("classes", [])]
        
        if "Global_Ecosystem" not in classes:
            print("Global_Ecosystem class not found. Creating it...")
            create_global_ecosystem_class(client)
        else:
            print("Global_Ecosystem class already exists.")
    except Exception as e:
        print(f"Error checking schema: {str(e)}")
        raise

def create_global_ecosystem_class(client):
    """Create the Global_Ecosystem class in Weaviate"""
    try:
        class_obj = {
            "class": "Global_Ecosystem",
            "vectorizer": "text2vec-openai",
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
        print("Created Weaviate class: Global_Ecosystem")
    except Exception as e:
        print(f"Error creating Global_Ecosystem class: {str(e)}")
        raise

def add_ecosystem_partner(client):
    """Add a sample ecosystem partner directly to Weaviate"""
    try:
        # Generate a partner ID
        partner_id = str(uuid.uuid4())
        
        # Sample partner data
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
        content = f"Partner name: {partner_data.get('name', '')}\n"
        content += f"Bio: {partner_data.get('bio', '')}\n"
        content += f"Expertise: {', '.join(partner_data.get('expertise', []))}\n"
        content += f"Case studies: {partner_data.get('case_studies', '')}\n"
        
        # Add content to partner_data
        partner_data["content"] = content
        
        # Add to Weaviate
        print("Adding ecosystem partner to Weaviate...")
        obj_id = client.data_object.create(
            class_name="Global_Ecosystem",
            data_object=partner_data
        )
        
        print(f"Successfully added partner with ID: {obj_id}")
        return obj_id
    except Exception as e:
        print(f"Error adding ecosystem partner: {str(e)}")
        raise

def search_ecosystem_partners(client, query="supply chain experts"):
    """Search for ecosystem partners using the provided query"""
    try:
        print(f"\nSearching for ecosystem partners with query: '{query}'...")
        
        # Create a more comprehensive search by combining the original query with expanded context
        expanded_query = f"Expert in {query}"
        
        # Define properties to retrieve
        properties = [
            "name", "bio", "expertise", "certifications", "case_studies",
            "website", "contact_info", "budget_tier", "partner_id",
            "tags", "content", "tenant_id"
        ]
        
        # Build and execute query
        near_text = {"concepts": [expanded_query]}
        query_builder = (
            client.query
            .get("Global_Ecosystem", properties)
            .with_near_text(near_text)
            .with_limit(5)
            .with_additional(["id", "certainty"])
        )
        
        result = query_builder.do()
        
        # Process results
        partners = []
        for res in result.get("data", {}).get("Get", {}).get("Global_Ecosystem", []):
            partners.append({
                "id": res["_additional"]["id"],
                "partner_id": res.get("partner_id", ""),
                "name": res.get("name", "Unknown Partner"),
                "bio": res.get("bio", ""),
                "expertise": res.get("expertise", []),
                "certifications": res.get("certifications", []),
                "case_studies": res.get("case_studies", ""),
                "website": res.get("website", ""),
                "contact_info": res.get("contact_info", ""),
                "budget_tier": res.get("budget_tier", ""),
                "tags": res.get("tags", []),
                "content": res.get("content", ""),
                "tenant_id": res.get("tenant_id", "default"),
                "relevance_score": res["_additional"]["certainty"]
            })
        
        # Print results
        print(f"Found {len(partners)} ecosystem partners matching the query.")
        for i, partner in enumerate(partners):
            print(f"\nPartner {i+1}: {partner.get('name', 'Unknown')}")
            print(f"Expertise: {', '.join(partner.get('expertise', []))}")
            print(f"Bio: {partner.get('bio', 'No bio available')[:100]}...")
            print(f"Relevance Score: {partner.get('relevance_score', 0)}")
        
        return partners
    except Exception as e:
        print(f"Error searching ecosystem partners: {str(e)}")
        return []

def main():
    """Main function to run the workflow"""
    try:
        # Create Weaviate client
        client = create_weaviate_client()
        
        # Check if the Global_Ecosystem class exists
        check_global_ecosystem_class(client)
        
        # Add a sample ecosystem partner
        obj_id = add_ecosystem_partner(client)
        
        # Wait for indexing to complete
        print("\nWaiting for indexing to complete...")
        time.sleep(5)
        
        # Search for ecosystem partners
        partners = search_ecosystem_partners(client)
        
        # Format the response like the API would
        api_response = {
            "query": "supply chain experts",
            "partners": []
        }
        
        for partner in partners:
            api_response["partners"].append({
                "partner_id": partner.get("partner_id", ""),
                "name": partner.get("name", ""),
                "bio": partner.get("bio", ""),
                "expertise": partner.get("expertise", []),
                "certifications": partner.get("certifications", []),
                "case_studies": partner.get("case_studies", ""),
                "website": partner.get("website", ""),
                "contact_info": partner.get("contact_info", ""),
                "budget_tier": partner.get("budget_tier", ""),
                "tags": partner.get("tags", []),
                "relevance_score": partner.get("relevance_score", 0.0),
                "citation_id": partner.get("id", "")
            })
        
        # Save the response to a file
        with open("ecosystem_partners_response.json", "w") as f:
            json.dump(api_response, f, indent=2)
        
        print("\nSaved API-like response to ecosystem_partners_response.json")
        
    except Exception as e:
        print(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main()