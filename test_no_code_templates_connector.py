#!/usr/bin/env python3
"""
Test script for No-Code Templates Connector

This script tests the NoCodeTemplatesClient connector that sends template data
to the external service running at http://192.168.0.98:8000/api/no-code-templates
"""

import asyncio
import sys
from datetime import datetime, UTC

# Add src to path
sys.path.insert(0, '.')

from src.data_stores.global_tools_client import NoCodeTemplatesClient, NoCodeTemplate, NoCodeTemplateCategory


async def test_no_code_template_connector():
    """Test sending a no-code template to the external service"""
    
    print("\n" + "="*80)
    print("Testing No-Code Templates Connector")
    print("="*80 + "\n")
    
    # Create a sample no-code template
    template = NoCodeTemplate(
        name="Customer Onboarding Workflow",
        source_url="https://templates.example.com/customer-onboarding",
        platform="Zapier",
        use_cases=[
            "Automate customer onboarding process",
            "Send welcome emails",
            "Create customer records in CRM"
        ],
        short_description="Streamline your customer onboarding with automated workflows",
        complexity="Intermediate",
        categories=NoCodeTemplateCategory(
            primary="Business Automation",
            secondary=["CRM Integration", "Email Automation", "Customer Management"]
        ),
        tags=["automation", "onboarding", "crm", "email"],
        detailed_description="This comprehensive template automates the entire customer onboarding process. It includes multi-step workflows for welcome emails, CRM record creation, and automated follow-ups. Perfect for businesses looking to scale their customer acquisition.",
        prerequisites=[
            "Active Zapier account",
            "Connected CRM system (Salesforce, HubSpot, or similar)",
            "Email service provider (Gmail, SendGrid, etc.)"
        ],
        estimated_time="30-45 minutes"
    )
    
    # Initialize client
    print("Initializing NoCodeTemplatesClient...")
    client = NoCodeTemplatesClient()
    print(f"Client configured with endpoint: {client.endpoint}\n")
    
    # Send template to service
    try:
        print("Sending no-code template to external service...\n")
        result = await client.post_no_code_template(template)
        
        print("\n" + "="*80)
        print("SUCCESS - Template sent to service!")
        print("="*80)
        print(f"\nResponse: {result}\n")
        
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print("ERROR - Failed to send template")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        
        return False


async def main():
    """Main test execution"""
    success = await test_no_code_template_connector()
    
    if success:
        print("\n✅ No-Code Templates Connector test PASSED")
        return 0
    else:
        print("\n❌ No-Code Templates Connector test FAILED")
        print("\nNote: Make sure the external service is running at BACKEND_SERVICE_URL")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
