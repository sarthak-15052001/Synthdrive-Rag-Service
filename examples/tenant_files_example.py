"""
Tenant Files Search Example

This example demonstrates how to use the tenant files search functionality
in the SynthDrive RAG service. It shows how to:

1. Upload a file for a specific organization
2. Search for content within that organization's files
3. Generate a prompt for LLM processing with proper citations
4. Use the prompt with an LLM to get a response

Requirements:
- Running SynthDrive RAG service
- API token for authentication
- Access to an LLM (this example uses OpenAI)
"""

import os
import requests
import json
import time
from datetime import datetime
import openai

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your SynthDrive RAG service URL
API_TOKEN = os.environ.get("SYNTHDRIVE_API_TOKEN", "your_api_token_here")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")

# Set up OpenAI client
openai.api_key = OPENAI_API_KEY

# Helper functions
def upload_file(file_path, organization_id, tenant_id="default", tags=None):
    """
    Upload a file to the tenant files storage.
    
    Args:
        file_path: Path to the file to upload
        organization_id: Organization ID for isolation
        tenant_id: Tenant ID (default: "default")
        tags: Optional list of tags for the file
        
    Returns:
        Response JSON with job_id
    """
    url = f"{API_BASE_URL}/ingest/tenant-file"
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        
        data = {
            'organization_id': organization_id,
            'tenant_id': tenant_id
        }
        
        if tags:
            data['file_tags'] = ','.join(tags)
        
        response = requests.post(
            url,
            files=files,
            data=data,
            headers={'Authorization': f'Bearer {API_TOKEN}'}
        )
        
        return response.json()

def search_files(query, organization_id, tenant_id="default", filters=None, limit=5):
    """
    Search for files in the tenant files storage.
    
    Args:
        query: Search query
        organization_id: Organization ID for isolation
        tenant_id: Tenant ID (default: "default")
        filters: Optional additional filters
        limit: Maximum number of results to return
        
    Returns:
        Response JSON with search results
    """
    url = f"{API_BASE_URL}/tenant-files/search"
    
    payload = {
        "query": query,
        "organization_id": organization_id,
        "tenant_id": tenant_id,
        "filters": filters or {},
        "limit": limit
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        }
    )
    
    return response.json()

def search_with_prompt(query, organization_id, tenant_id="default", filters=None, limit=5):
    """
    Search for files and generate a prompt for LLM processing.
    
    Args:
        query: Search query
        organization_id: Organization ID for isolation
        tenant_id: Tenant ID (default: "default")
        filters: Optional additional filters
        limit: Maximum number of results to return
        
    Returns:
        Response JSON with search results and prompt
    """
    url = f"{API_BASE_URL}/tenant-files/search-with-prompt"
    
    payload = {
        "query": query,
        "organization_id": organization_id,
        "tenant_id": tenant_id,
        "filters": filters or {},
        "limit": limit
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        }
    )
    
    return response.json()

def get_llm_response(prompt):
    """
    Get a response from the LLM using the generated prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        LLM response text
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def main():
    # Example organization and tenant
    organization_id = "example-org-123"
    tenant_id = "default"
    
    # Step 1: Create a sample file
    print("Creating a sample file...")
    sample_file_path = "sample_strategic_plan.pdf"
    
    with open(sample_file_path, "w") as f:
        f.write(f"""
STRATEGIC PLAN 2024-2026
Organization: {organization_id}

EXECUTIVE SUMMARY
This document outlines the strategic plan for {organization_id} for the years 2024-2026.

STRATEGIC GOALS
1. Increase market share by 15% by end of 2024
2. Launch 3 new product lines by Q2 2025
3. Expand into European markets by Q3 2025
4. Achieve carbon neutrality by end of 2026

FINANCIAL TARGETS
- Revenue: $50M (2024), $75M (2025), $100M (2026)
- Profit Margin: 18% (2024), 20% (2025), 22% (2026)
- R&D Investment: 12% of revenue

RISK ASSESSMENT
- Market competition from emerging startups
- Supply chain disruptions
- Regulatory changes in target markets

CONFIDENTIAL - FOR INTERNAL USE ONLY
        """)
    
    # Step 2: Upload the file
    print(f"Uploading file for organization {organization_id}...")
    upload_response = upload_file(
        file_path=sample_file_path,
        organization_id=organization_id,
        tenant_id=tenant_id,
        tags=["strategic", "plan", "2024"]
    )
    
    print(f"Upload response: {json.dumps(upload_response, indent=2)}")
    
    # Wait for indexing
    print("Waiting 5 seconds for indexing...")
    time.sleep(5)
    
    # Step 3: Search for files
    print(f"Searching for strategic goals...")
    search_response = search_files(
        query="strategic goals for 2024",
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    print(f"Found {len(search_response.get('files', []))} results")
    
    # Step 4: Search with prompt generation
    print(f"Generating prompt for LLM...")
    prompt_response = search_with_prompt(
        query="What are our financial targets for 2025?",
        organization_id=organization_id,
        tenant_id=tenant_id
    )
    
    prompt = prompt_response.get("prompt", "")
    print(f"Generated prompt length: {len(prompt)} characters")
    print("Prompt preview:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    # Step 5: Get LLM response
    if prompt:
        print("\nGetting LLM response...")
        llm_response = get_llm_response(prompt)
        
        print("\nLLM Response:")
        print(llm_response)
    
    # Clean up
    print("\nCleaning up...")
    os.remove(sample_file_path)
    print("Sample file removed")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()