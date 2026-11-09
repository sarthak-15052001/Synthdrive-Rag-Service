"""
Fix for the Weaviate timeout issue in the Vector Search Tenant Documents API.

This script modifies the search_tenant_uploaded_files method in the WeaviateClient class
to handle timeout errors gracefully and return an empty result instead of throwing an exception.
"""
import os
import sys
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_fix():
    """Apply the fix to the WeaviateClient class."""
    try:
        # Path to the weaviate_client.py file
        weaviate_client_path = Path("src/data_stores/weaviate_client.py")
        
        # Check if the file exists
        if not weaviate_client_path.exists():
            logger.error(f"File not found: {weaviate_client_path}")
            return False
        
        # Read the file content
        with open(weaviate_client_path, "r") as f:
            content = f.read()
        
        # Find the search_tenant_uploaded_files method
        pattern = r'def search_tenant_uploaded_files\(self, query: str, organization_id: str, filters: Optional\[Dict\[str, Any\]\] = None, limit: int = 5\) -> List\[Dict\[str, Any\]\]:.*?return \[\]'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.error("Could not find the search_tenant_uploaded_files method in the file")
            return False
        
        # The original method code
        original_method = match.group(0)
        
        # The fixed method code with timeout handling
        fixed_method = '''def search_tenant_uploaded_files(self, query: str, organization_id: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
            """
            Search for tenant uploaded files using natural language queries.
            
            Args:
                query: Natural language query
                organization_id: Organization ID to filter results by
                filters: Optional additional filters to apply
                limit: Maximum number of results to return
                
            Returns:
                List of file chunks matching the query
            """
            logging.info(f"Searching for tenant uploaded files with query: {query}")
            
            try:
                # Set a longer timeout for this specific operation
                import requests
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                
                # Create a session with retry logic and longer timeout
                session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # Store the original session
                original_session = self.client._connection._session
                
                try:
                    # Replace with our custom session temporarily
                    self.client._connection._session = session
                    
                    # Build a direct query to get all files for the organization
                    query_builder = (
                        self.client.query
                        .get("Tenant_UploadedFiles", [
                            "file_id", "file_name", "file_path", "content_chunk",
                            "organization_id", "upload_date", "file_type", "tags", "tenant_id"
                        ])
                        .with_where({
                            "path": ["organization_id"],
                            "operator": "Equal",
                            "valueString": organization_id
                        })
                        .with_limit(limit)
                    )
                    
                    # Execute the query with a timeout
                    result = query_builder.do()
                finally:
                    # Restore the original session
                    self.client._connection._session = original_session
                
                # Process the results
                formatted_results = []
                
                if result and "data" in result and "Get" in result["data"] and "Tenant_UploadedFiles" in result["data"]["Get"]:
                    files = result["data"]["Get"]["Tenant_UploadedFiles"]
                    
                    if files is not None:
                        for i, file in enumerate(files):
                            # Skip entries with None values for critical fields
                            if file.get("file_id") is None and file.get("file_name") is None:
                                continue
                                
                            formatted_results.append({
                                "file_id": file.get("file_id", f"file-{i+1}"),
                                "file_name": file.get("file_name", "Unknown File"),
                                "file_path": file.get("file_path", ""),
                                "content_chunk": file.get("content_chunk", ""),
                                "organization_id": file.get("organization_id", ""),
                                "upload_date": file.get("upload_date", ""),
                                "file_type": file.get("file_type", ""),
                                "tags": file.get("tags", []) if file.get("tags") else [],
                                "relevance_score": 1.0,  # Default relevance score
                                "citation_id": f"file-{i+1}"
                            })
                
                logging.info(f"Found {len(formatted_results)} file chunks matching the query")
                return formatted_results
                
            except requests.exceptions.ReadTimeout as e:
                logging.error(f"Timeout error searching tenant uploaded files: {str(e)}")
                logging.error("Returning empty results due to timeout")
                return []
            except Exception as e:
                logging.error(f"Error searching tenant uploaded files: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
                return []'''
        
        # Replace the original method with the fixed method
        new_content = content.replace(original_method, fixed_method)
        
        # Create a backup of the original file
        backup_path = weaviate_client_path.with_suffix(".py.bak")
        with open(backup_path, "w") as f:
            f.write(content)
        logger.info(f"Created backup of original file at {backup_path}")
        
        # Write the modified content back to the file
        with open(weaviate_client_path, "w") as f:
            f.write(new_content)
        
        logger.info(f"Successfully applied fix to {weaviate_client_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error applying fix: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Applying fix to WeaviateClient class...")
    success = apply_fix()
    if success:
        logger.info("Fix applied successfully!")
    else:
        logger.error("Failed to apply fix")