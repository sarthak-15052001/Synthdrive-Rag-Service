import requests
import json
import time
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Replace with your actual token
TOKEN = "your_token_here"

# Headers for all requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

def add_ecosystem_partner():
    """Add a sample ecosystem partner to the system"""
    url = f"{BASE_URL}/ingest/global-ecosystem-partner"
    
    # Sample partner data
    partner_data = {
        "tenant_id": "default",
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
        "tags": [
            "supply chain",
            "logistics",
            "consulting",
            "enterprise"
        ]
    }
    
    try:
        print("Adding ecosystem partner...")
        response = requests.post(url, headers=HEADERS, json=partner_data)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Successfully added partner with ID: {result.get('partner_id', 'unknown')}")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Error adding partner: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception occurred while adding partner: {str(e)}")
        return False

def search_ecosystem_partners(query="supply chain experts"):
    """Search for ecosystem partners using the provided query"""
    url = f"{BASE_URL}/rag/ecosystem-partners/search"
    
    # Search payload
    payload = {
        "tenant_id": "default",
        "query": query,
        "filters": {},
        "limit": 5
    }
    
    try:
        print(f"\nSearching for ecosystem partners with query: '{query}'...")
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\nSearch Results:")
            print(json.dumps(result, indent=2))
            
            # Print summary of results
            if "partners" in result:
                print(f"\nFound {len(result['partners'])} ecosystem partners matching the query.")
                
                # Print details of each partner
                for i, partner in enumerate(result["partners"]):
                    print(f"\nPartner {i+1}: {partner.get('name', 'Unknown')}")
                    print(f"Expertise: {', '.join(partner.get('expertise', []))}")
                    print(f"Bio: {partner.get('bio', 'No bio available')[:100]}...")
                    print(f"Relevance Score: {partner.get('relevance_score', 0)}")
            
            return result
        else:
            print(f"Error searching partners: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Exception occurred while searching partners: {str(e)}")
        return None

def main():
    """Main function to run the workflow"""
    # Check if we should skip adding a partner
    skip_add = "--skip-add" in sys.argv
    
    if not skip_add:
        success = add_ecosystem_partner()
        if success:
            print("\nWaiting for indexing to complete...")
            time.sleep(5)  # Give some time for indexing
    
    # Search with default query
    search_result = search_ecosystem_partners()
    
    # Try a different query if specified
    if len(sys.argv) > 1 and sys.argv[1] != "--skip-add":
        custom_query = sys.argv[1]
        search_ecosystem_partners(custom_query)

if __name__ == "__main__":
    main()