import json
import requests
import time
from pprint import pprint

# Server URL
BASE_URL = "http://localhost:8000"

def test_synthesizer_with_payload(payload_name, payload):
    """
    Test the Synthesizer endpoint with a specific payload.
    
    Args:
        payload_name: Name of the payload for identification
        payload: The request payload to send
    
    Returns:
        The response from the API
    """
    print(f"\n{'='*80}")
    print(f"Testing Synthesizer with payload: {payload_name}")
    print(f"{'='*80}")
    
    # Send the request to the Synthesizer endpoint
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/rag/synthesizer",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(f"\nSynthesizer Response (took {end_time - start_time:.2f} seconds):")
            print(f"Query: {result.get('query')}")
            print(f"Organization ID: {result.get('organization_id')}")
            print("\nFinal Answer:")
            print(result.get('final_answer'))
            return result
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """
    Main function to test the Synthesizer API with different payloads.
    """
    print("Starting Synthesizer API Tests...")
    
    # Load the sample payloads
    try:
        with open('synthesizer_payloads.json', 'r') as f:
            payload_collection = json.load(f)
    except Exception as e:
        print(f"Error loading payloads: {str(e)}")
        return
    
    results = {}
    
    # Test each payload
    for payload_item in payload_collection:
        payload_name = payload_item.get('payload_name')
        payload = payload_item.get('payload')
        
        if not payload_name or not payload:
            print("Invalid payload item, skipping...")
            continue
        
        result = test_synthesizer_with_payload(payload_name, payload)
        results[payload_name] = result
    
    # Summary
    print("\n\n")
    print(f"{'='*80}")
    print("SUMMARY OF RESULTS")
    print(f"{'='*80}")
    
    for name, result in results.items():
        status = "✅ Success" if result else "❌ Failed"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()