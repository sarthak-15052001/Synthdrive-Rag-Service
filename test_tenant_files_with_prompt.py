import os
import json
import asyncio
import requests
import argparse
from typing import Dict, Any, List
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Default test data
DEFAULT_TEST_FILE_PATH = "corporate_intelligence.txt"
DEFAULT_TEST_ORG_ID = "test-org-1"
DEFAULT_TEST_TENANT_ID = "default"

class TenantFilesPromptTest:
    """Test class for tenant files upload and search with prompt functionality"""
    
    def __init__(self, base_url=BASE_URL, file_path=None, org_id=None, tenant_id=None):
        self.base_url = base_url
        self.file_path = file_path or DEFAULT_TEST_FILE_PATH
        self.org_id = org_id or DEFAULT_TEST_ORG_ID
        self.tenant_id = tenant_id or DEFAULT_TEST_TENANT_ID
        self.job_id = None
        self.uploaded_files = []
        
        # Create test file if it doesn't exist
        if not os.path.exists(self.file_path):
            self._create_test_file()
    
    def _create_test_file(self):
        """Create a test file with corporate intelligence content"""
        print(f"Creating test file: {self.file_path}")
        
        # Sample corporate intelligence content
        content = f"""
        CORPORATE INTELLIGENCE REPORT
        Organization: {self.org_id}
        Date: {datetime.now().strftime('%Y-%m-%d')}
        
        EXECUTIVE SUMMARY
        This document contains confidential corporate intelligence for {self.org_id}.
        The information includes financial data, strategic initiatives, and market analysis.
        
        FINANCIAL PERFORMANCE
        Revenue: $125M (Q3 2023)
        Growth: 15% YoY
        EBITDA Margin: 28%
        
        STRATEGIC INITIATIVES
        1. Expansion into APAC region by Q2 2024
        2. Launch of new product line "Quantum Series"
        3. Digital transformation of supply chain operations
        
        MARKET ANALYSIS
        - Current market share: 23%
        - Main competitors: CompA (31%), CompB (18%), CompC (12%)
        - Growth opportunities in healthcare and financial services verticals
        
        CONFIDENTIAL - FOR INTERNAL USE ONLY
        """
        
        # Write content to file
        with open(self.file_path, "w") as f:
            f.write(content)
    
    async def upload_file(self, tags="corporate,intelligence,financial"):
        """Upload a tenant file"""
        print(f"\n=== Uploading Tenant File for Organization {self.org_id} ===")
        
        try:
            # Upload the file
            with open(self.file_path, "rb") as f:
                files = {"file": (os.path.basename(self.file_path), f, "text/plain")}
                
                # Use URL parameters
                url = f"{self.base_url}/rag/ingest/tenant-file?organization_id={self.org_id}&tenant_id={self.tenant_id}&file_tags={tags}"
                
                print(f"Uploading file to URL: {url}")
                
                response = requests.post(
                    url,
                    files=files
                )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                self.job_id = result.get("job_id")
                print(f"✅ File uploaded successfully with job ID: {self.job_id}")
                return self.job_id
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
            print(f"❌ Exception during file upload: {str(e)}")
            return None
    
    async def search_files(self, query="financial data strategic initiatives", wait_time=10):
        """Search for tenant files"""
        print(f"\n=== Searching Tenant Files for Organization {self.org_id} ===")
        
        # Wait for ingestion to complete if we just uploaded a file
        if self.job_id:
            print(f"Waiting {wait_time} seconds for ingestion job {self.job_id} to complete...")
            await asyncio.sleep(wait_time)
        
        # Search request data
        search_data = {
            "query": query,
            "organization_id": self.org_id,
            "tenant_id": self.tenant_id,
            "filters": {},
            "limit": 10
        }
        
        print(f"Search query: '{query}'")
        
        # Make the search request
        response = requests.post(
            f"{self.base_url}/rag/tenant-files/search",
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
                print(f"  Content Chunk: {file.get('content_chunk')[:100]}...")
                print(f"  Relevance Score: {file.get('relevance_score')}")
                print(f"  Citation ID: {file.get('citation_id')}")
            
            self.uploaded_files = files
            return files
        else:
            print(f"❌ Search failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return []
    
    async def search_with_prompt(self, query="financial data strategic initiatives", wait_time=10):
        """Search for tenant files with prompt generation"""
        print(f"\n=== Searching Tenant Files with Prompt for Organization {self.org_id} ===")
        
        # Wait for ingestion to complete if we just uploaded a file
        if self.job_id:
            print(f"Waiting {wait_time} seconds for ingestion job {self.job_id} to complete...")
            await asyncio.sleep(wait_time)
        
        # Search request data
        search_data = {
            "query": query,
            "organization_id": self.org_id,
            "tenant_id": self.tenant_id,
            "filters": {},
            "limit": 10
        }
        
        print(f"Search query: '{query}'")
        
        # Make the search request
        response = requests.post(
            f"{self.base_url}/rag/tenant-files/search-with-prompt",
            json=search_data
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            search_results = result.get("search_results", {})
            prompt = result.get("prompt", "")
            
            files = search_results.get("files", [])
            print(f"✅ Search with prompt successful, found {len(files)} files")
            
            # Print file details
            for i, file in enumerate(files):
                print(f"\nFile {i+1}:")
                print(f"  File ID: {file.get('file_id')}")
                print(f"  File Name: {file.get('file_name')}")
                print(f"  Content Chunk: {file.get('content_chunk')[:100]}...")
                print(f"  Relevance Score: {file.get('relevance_score')}")
                print(f"  Citation ID: {file.get('citation_id')}")
            
            # Print prompt
            print("\n=== Generated Prompt ===")
            print(f"Prompt length: {len(prompt)} characters")
            print("Prompt preview:")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            
            self.uploaded_files = files
            return result
        else:
            print(f"❌ Search with prompt failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return {}
    
    async def test_organization_isolation(self, other_org_id="test-org-2"):
        """Test that files are isolated by organization_id"""
        print(f"\n=== Testing Organization Isolation: {self.org_id} vs {other_org_id} ===")
        
        # Search request for other organization
        search_data = {
            "query": "financial data strategic initiatives",
            "organization_id": other_org_id,  # Different organization
            "tenant_id": self.tenant_id,
            "filters": {},
            "limit": 10
        }
        
        # Make the search request
        response = requests.post(
            f"{self.base_url}/rag/tenant-files/search",
            json=search_data
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            files = result.get("files", [])
            
            if len(files) == 0:
                print(f"✅ Organization isolation successful: No files found for {other_org_id}")
                return True
            else:
                print(f"❌ Organization isolation failed: Found {len(files)} files for {other_org_id}")
                return False
        else:
            print(f"❌ Search failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    
    async def run_all_tests(self, wait_time=10):
        """Run all tests in sequence"""
        print("\n=== Running All Tenant Files Tests with Prompt ===")
        
        # Test file upload
        job_id = await self.upload_file()
        
        if not job_id:
            print("❌ File upload failed, cannot proceed with further tests")
            return False
        
        # Test file search
        files = await self.search_files(wait_time=wait_time)
        
        if not files or len(files) == 0:
            print("❌ File search failed, cannot proceed with further tests")
            return False
        
        # Test search with prompt
        prompt_result = await self.search_with_prompt(wait_time=1)  # Short wait since we already waited
        
        if not prompt_result:
            print("❌ Search with prompt failed")
            return False
        
        # Test organization isolation
        isolation_success = await self.test_organization_isolation()
        
        # Overall test result
        if files and prompt_result and isolation_success:
            print("\n✅ All tests passed successfully!")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
    
    def cleanup(self):
        """Clean up test files"""
        if os.path.exists(self.file_path) and self.file_path == DEFAULT_TEST_FILE_PATH:
            os.remove(self.file_path)
            print(f"Cleaned up test file: {self.file_path}")

async def main():
    """Main function to run the tests"""
    parser = argparse.ArgumentParser(description="Test tenant files search with prompt functionality")
    parser.add_argument("--url", default=BASE_URL, help="Base URL for the API")
    parser.add_argument("--file", default=DEFAULT_TEST_FILE_PATH, help="Path to test file")
    parser.add_argument("--org", default=DEFAULT_TEST_ORG_ID, help="Organization ID")
    parser.add_argument("--tenant", default=DEFAULT_TEST_TENANT_ID, help="Tenant ID")
    parser.add_argument("--wait", type=int, default=10, help="Wait time in seconds for ingestion")
    args = parser.parse_args()
    
    # Create test instance
    test = TenantFilesPromptTest(
        base_url=args.url,
        file_path=args.file,
        org_id=args.org,
        tenant_id=args.tenant
    )
    
    try:
        # Run all tests
        await test.run_all_tests(wait_time=args.wait)
    finally:
        # Clean up
        test.cleanup()

if __name__ == "__main__":
    print("Starting tenant files search with prompt tests...")
    asyncio.run(main())
    print("\nTests completed!")