import os
import json
import asyncio
import requests
from typing import Dict, Any, List

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Test data
TEST_FILE_PATH = "corporate_intelligence.txt"
TEST_ORG_ID = "test-org"
TEST_TENANT_ID = "default"

async def test_tenant_file_upload():
    """Test uploading a tenant file"""
    print("\n=== Testing Tenant File Upload ===")
    
    try:
        # Upload the file
        with open(TEST_FILE_PATH, "rb") as f:
            files = {"file": (TEST_FILE_PATH, f, "text/plain")}
            
            # Use URL parameters instead of form data
            url = f"{BASE_URL}/rag/ingest/tenant-file?organization_id={TEST_ORG_ID}&tenant_id={TEST_TENANT_ID}&file_tags=financial,report,2023"
            
            print(f"Uploading file to URL: {url}")
            print(f"Request files: {files}")
            
            response = requests.post(
                url,
                files=files
            )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ File uploaded successfully with job ID: {job_id}")
            return job_id
        else:
            print(f"❌ File upload failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
            # Try to get more detailed error information
            try:
                error_detail = response.json()
                print(f"Error details: {error_detail}")
            except:
                print("Could not parse error details")
                
            return None
    
    except Exception as e:
        print(f"Error during file upload: {str(e)}")
        return None

async def test_tenant_file_search(job_id: str = None):
    """Test searching for tenant files"""
    print("\n=== Testing Tenant File Search ===")
    
    # Wait a bit for ingestion to complete if we just uploaded a file
    if job_id:
        print(f"Waiting for ingestion job {job_id} to complete...")
        
        # Try multiple times with increasing wait times
        for wait_time in [5, 10, 15, 20]:
            print(f"Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            # Search request data
            search_data = {
                "query": "financial report 2023",
                "organization_id": TEST_ORG_ID,
                "tenant_id": TEST_TENANT_ID,
                "filters": {},
                "limit": 5
            }
            
            # Make the search request
            response = requests.post(
                f"{BASE_URL}/rag/tenant-files/search",
                json=search_data
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                files = result.get("files", [])
                print(f"Search attempt after {wait_time}s: found {len(files)} files")
                
                if len(files) > 0:
                    print(f"✅ Search successful, found {len(files)} files")
                    
                    # Print file details
                    for i, file in enumerate(files):
                        print(f"\nFile {i+1}:")
                        print(f"  File ID: {file.get('file_id')}")
                        print(f"  File Name: {file.get('file_name')}")
                        print(f"  Content Chunk: {file.get('content_chunk')[:50]}...")
                        print(f"  Relevance Score: {file.get('relevance_score')}")
                    
                    return files
            else:
                print(f"❌ Search failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
        
        # If we get here, we didn't find any files after all attempts
        print("❌ No files found after multiple attempts")
        return []
    else:
        # Just do a single search if no job_id was provided
        search_data = {
            "query": "financial report 2023",
            "organization_id": TEST_ORG_ID,
            "tenant_id": TEST_TENANT_ID,
            "filters": {},
            "limit": 5
        }
        
        # Make the search request
        response = requests.post(
            f"{BASE_URL}/rag/tenant-files/search",
            json=search_data
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            print(f"✅ Search successful, found {len(files)} files")
            
            # Print file details
            for i, file in enumerate(files):
                print(f"\nFile {i+1}:")
                print(f"  File ID: {file.get('file_id')}")
                print(f"  File Name: {file.get('file_name')}")
                print(f"  Content Chunk: {file.get('content_chunk')[:50]}...")
                print(f"  Relevance Score: {file.get('relevance_score')}")
            
            return files
        else:
            print(f"❌ Search failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return []

async def test_get_file_by_id(file_id: str):
    """Test getting a specific file by ID"""
    print(f"\n=== Testing Get File by ID: {file_id} ===")
    
    # Make the request
    response = requests.get(
        f"{BASE_URL}/rag/tenant-files/{file_id}",
        params={"organization_id": TEST_ORG_ID, "tenant_id": TEST_TENANT_ID}
    )
    
    # Check response
    if response.status_code == 200:
        file = response.json()
        print(f"✅ Successfully retrieved file: {file.get('file_name')}")
        print(f"  Content Chunk: {file.get('content_chunk')[:50]}...")
        return file
    else:
        print(f"❌ Get file failed with status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None

async def test_organization_isolation():
    """Test organization isolation"""
    print("\n=== Testing Organization Isolation ===")
    
    # Search with a different organization ID
    search_data = {
        "query": "financial report 2023",
        "organization_id": "different-org",  # Different org ID
        "tenant_id": TEST_TENANT_ID,
        "filters": {},
        "limit": 5
    }
    
    # Make the search request
    response = requests.post(
        f"{BASE_URL}/rag/tenant-files/search",
        json=search_data
    )
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        files = result.get("files", [])
        if len(files) == 0:
            print("✅ Organization isolation verified - no files found for different organization")
        else:
            print(f"❌ Organization isolation failed - found {len(files)} files for different organization")
        
        return files
    else:
        print(f"❌ Search failed with status code: {response.status_code}")
        print(f"Error: {response.text}")
        return []

async def run_tests():
    """Run all tests"""
    # Test file upload
    job_id = await test_tenant_file_upload()
    
    # Test file search
    files = await test_tenant_file_search(job_id)
    
    # Test get file by ID if we found any files
    if files and len(files) > 0:
        file_id = files[0].get("file_id")
        await test_get_file_by_id(file_id)
    
    # Test organization isolation
    await test_organization_isolation()

if __name__ == "__main__":
    print("Starting tenant file search tests...")
    asyncio.run(run_tests())
    print("\nTests completed!")