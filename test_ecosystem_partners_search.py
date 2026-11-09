import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/rag/ecosystem-partners/search"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"  # Replace with your actual token
}

# Payload for the request
payload = {
    "tenant_id": "default",
    "query": "supply chain experts",
    "filters": {
        # Optional filters can be added here
        # "budget_tier": "enterprise"
    },
    "limit": 5
}

# Make the request
try:
    response = requests.post(url, headers=headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        
        # Pretty print the response
        print("API Response:")
        print(json.dumps(result, indent=2))
        
        # Print the number of partners found
        if "partners" in result:
            print(f"\nFound {len(result['partners'])} ecosystem partners matching the query.")
            
            # Print details of each partner
            for i, partner in enumerate(result["partners"]):
                print(f"\nPartner {i+1}: {partner.get('name', 'Unknown')}")
                print(f"Expertise: {', '.join(partner.get('expertise', []))}")
                print(f"Bio: {partner.get('bio', 'No bio available')[:100]}...")
                print(f"Relevance Score: {partner.get('relevance_score', 0)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception occurred: {str(e)}")