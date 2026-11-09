import weaviate
import os
from dotenv import load_dotenv

def search_products():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        # Initialize the client
        client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
        )

        print("Testing different search queries:\n")

        # 1. Search by category
        print("1. Products in Electronics category:")
        result = (
            client.query
            .get("Product", ["name", "price", "description"])
            .with_where({
                "path": ["category"],
                "operator": "Equal",
                "valueString": "Electronics"
            })
            .do()
        )
        for item in result['data']['Get']['Product']:
            print(f"- {item['name']} (${item['price']})")
            print(f"  Description: {item['description']}\n")

        # 2. Search by price range
        print("\n2. Products under $100:")
        result = (
            client.query
            .get("Product", ["name", "price", "category"])
            .with_where({
                "path": ["price"],
                "operator": "LessThan",
                "valueNumber": 100.0
            })
            .do()
        )
        for item in result['data']['Get']['Product']:
            print(f"- {item['name']} (${item['price']}) - {item['category']}")

        # 3. Text search in description
        print("\n3. Search for products containing 'wireless' in description:")
        result = (
            client.query
            .get("Product", ["name", "description", "price"])
            .with_where({
                "path": ["description"],
                "operator": "Like",
                "valueString": "*wireless*"
            })
            .do()
        )
        
        if result and 'data' in result and 'Get' in result['data'] and 'Product' in result['data']['Get']:
            products = result['data']['Get']['Product']
            if products:
                for item in products:
                    print(f"- {item['name']} (${item['price']})")
                    print(f"  Description: {item['description']}\n")
            else:
                print("No products found matching the search criteria.")
        else:
            print("No results found")

        # 4. Search by name pattern
        print("\n4. Products with 'Pro' in the name:")
        result = (
            client.query
            .get("Product", ["name", "price", "category"])
            .with_where({
                "path": ["name"],
                "operator": "Like",
                "valueString": "*Pro*"
            })
            .do()
        )
        for item in result['data']['Get']['Product']:
            print(f"- {item['name']} (${item['price']}) - {item['category']}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    search_products()