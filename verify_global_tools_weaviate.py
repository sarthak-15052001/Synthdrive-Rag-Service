"""
Script to verify Global_Tools data in Weaviate.
This shows all fields stored for the tools in Weaviate.
"""

import weaviate
import json
from datetime import datetime

# Connect to Weaviate
client = weaviate.Client(
    url="http://localhost:8080",  # Update with your Weaviate URL
    additional_headers={
        "X-OpenAI-Api-Key": "your-openai-api-key-here"  # Update with your OpenAI API key
    }
)

def check_schema():
    """Check the GlobalTools schema"""
    print("=" * 80)
    print("GLOBAL_TOOLS SCHEMA")
    print("=" * 80)
    
    try:
        schema = client.schema.get("Global_Tools")
        print(f"\nClass Name: {schema.get('class')}")
        print(f"Vectorizer: {schema.get('vectorizer')}")
        print(f"\nProperties:")
        
        for prop in schema.get('properties', []):
            print(f"  - {prop['name']}: {prop['dataType']} - {prop.get('description', 'No description')}")
        
        print(f"\nTotal Properties: {len(schema.get('properties', []))}")
    except Exception as e:
        print(f"Error getting schema: {str(e)}")

def list_all_tools():
    """List all tools in the Global_Tools collection"""
    print("\n" + "=" * 80)
    print("ALL TOOLS IN GLOBAL_TOOLS COLLECTION")
    print("=" * 80)
    
    try:
        result = client.query.get(
            "Global_Tools",
            [
                "name", "homepage_url", "last_scraped_at", "source_urls",
                "primary_category", "secondary_categories",
                "short_description", "detailed_description",
                "features_json", "differentiators",
                "subscriptions_json", "compliance_json",
                "documentation_links", "rating", "logo_url", "tags",
                "tenant_id"
            ]
        ).with_additional(["id", "creationTimeUnix"]).do()
        
        tools = result.get("data", {}).get("Get", {}).get("Global_Tools", [])
        
        if not tools:
            print("\n❌ No tools found in Global_Tools collection")
            return
        
        print(f"\n✅ Found {len(tools)} tool(s)")
        
        for i, tool in enumerate(tools, 1):
            print(f"\n{'─' * 80}")
            print(f"TOOL #{i}: {tool.get('name', 'Unnamed Tool')}")
            print(f"{'─' * 80}")
            
            # Print basic info
            print(f"ID: {tool.get('_additional', {}).get('id', 'N/A')}")
            print(f"Created: {datetime.fromtimestamp(tool.get('_additional', {}).get('creationTimeUnix', 0)).isoformat() if tool.get('_additional', {}).get('creationTimeUnix') else 'N/A'}")
            print(f"Tenant ID: {tool.get('tenant_id', 'N/A')}")
            
            # Print all field values
            print(f"\n📋 Field Values:")
            print(f"  Name: {tool.get('name', 'N/A')}")
            print(f"  Homepage URL: {tool.get('homepage_url', 'N/A')}")
            print(f"  Last Scraped: {tool.get('last_scraped_at', 'N/A')}")
            print(f"  Source URLs: {tool.get('source_urls', [])}")
            print(f"  Primary Category: {tool.get('primary_category', 'N/A')}")
            print(f"  Secondary Categories: {tool.get('secondary_categories', [])}")
            print(f"  Rating: {tool.get('rating', 'N/A')}")
            print(f"  Logo URL: {tool.get('logo_url', 'N/A')}")
            print(f"  Tags: {tool.get('tags', [])}")
            print(f"  Documentation Links: {tool.get('documentation_links', [])}")
            print(f"  Differentiators: {tool.get('differentiators', [])}")
            
            # Print descriptions (truncated)
            short_desc = tool.get('short_description', 'N/A')
            print(f"  Short Description: {short_desc[:100]}..." if len(short_desc) > 100 else f"  Short Description: {short_desc}")
            
            detailed_desc = tool.get('detailed_description', 'N/A')
            print(f"  Detailed Description: {detailed_desc[:100]}..." if len(detailed_desc) > 100 else f"  Detailed Description: {detailed_desc}")
            
            # Parse and print JSON fields
            print(f"\n📦 Complex Fields (JSON):")
            
            # Features
            features_json = tool.get('features_json', '[]')
            try:
                features = json.loads(features_json)
                print(f"  Features ({len(features)} total):")
                for feat in features:
                    print(f"    - {feat.get('name')}: {feat.get('description', 'No description')[:80]}...")
            except:
                print(f"  Features: Error parsing JSON")
            
            # Subscriptions
            subscriptions_json = tool.get('subscriptions_json', '[]')
            try:
                subscriptions = json.loads(subscriptions_json)
                print(f"  Subscriptions ({len(subscriptions)} plans):")
                for sub in subscriptions:
                    monthly = sub.get('price_monthly', 'Free')
                    print(f"    - {sub.get('plan_name')}: ${monthly}/month" if monthly else f"    - {sub.get('plan_name')}: Free")
            except:
                print(f"  Subscriptions: Error parsing JSON")
            
            # Compliance
            compliance_json = tool.get('compliance_json', '{}')
            try:
                compliance = json.loads(compliance_json)
                print(f"  Compliance:")
                print(f"    - GDPR Compliant: {compliance.get('gdpr_compliant', 'N/A')}")
                print(f"    - US Cloud Act Safe: {compliance.get('us_cloud_act_safe', 'N/A')}")
                print(f"    - Data Sovereignty: {compliance.get('data_sovereignty_options', [])}")
                print(f"    - Certifications: {compliance.get('certifications', [])}")
            except:
                print(f"  Compliance: Error parsing JSON")
        
        print(f"\n{'=' * 80}")
        
    except Exception as e:
        print(f"\n❌ Error listing tools: {str(e)}")
        import traceback
        traceback.print_exc()

def verify_specific_fields():
    """Verify that specific fields are present and not null"""
    print("\n" + "=" * 80)
    print("FIELD VERIFICATION")
    print("=" * 80)
    
    try:
        # Query just the tool names to get count
        result = client.query.get(
            "Global_Tools",
            ["name", "last_scraped_at", "features_json", "subscriptions_json", "compliance_json"]
        ).do()
        
        tools = result.get("data", {}).get("Get", {}).get("Global_Tools", [])
        
        if not tools:
            print("\n❌ No tools found for verification")
            return
        
        print(f"\nVerifying {len(tools)} tool(s)...")
        
        for i, tool in enumerate(tools, 1):
            print(f"\nTool #{i}: {tool.get('name')}")
            
            # Check last_scraped_at
            last_scraped = tool.get('last_scraped_at')
            if last_scraped:
                print(f"  ✅ last_scraped_at: {last_scraped}")
            else:
                print(f"  ❌ last_scraped_at: MISSING")
            
            # Check features_json
            features_json = tool.get('features_json')
            if features_json and features_json != '[]':
                try:
                    features = json.loads(features_json)
                    print(f"  ✅ features_json: {len(features)} features stored")
                except:
                    print(f"  ⚠️  features_json: Present but invalid JSON")
            else:
                print(f"  ❌ features_json: MISSING or empty")
            
            # Check subscriptions_json
            subscriptions_json = tool.get('subscriptions_json')
            if subscriptions_json and subscriptions_json != '[]':
                try:
                    subscriptions = json.loads(subscriptions_json)
                    print(f"  ✅ subscriptions_json: {len(subscriptions)} subscription plans stored")
                except:
                    print(f"  ⚠️  subscriptions_json: Present but invalid JSON")
            else:
                print(f"  ❌ subscriptions_json: MISSING or empty")
            
            # Check compliance_json
            compliance_json = tool.get('compliance_json')
            if compliance_json and compliance_json != '{}':
                try:
                    compliance = json.loads(compliance_json)
                    print(f"  ✅ compliance_json: {len(compliance)} compliance fields stored")
                except:
                    print(f"  ⚠️  compliance_json: Present but invalid JSON")
            else:
                print(f"  ❌ compliance_json: MISSING or empty")
        
    except Exception as e:
        print(f"\n❌ Error verifying fields: {str(e)}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GLOBAL TOOLS WEAVIATE VERIFICATION SCRIPT")
    print("=" * 80)
    
    # Check schema
    check_schema()
    
    # List all tools
    list_all_tools()
    
    # Verify specific fields
    verify_specific_fields()
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80 + "\n")
