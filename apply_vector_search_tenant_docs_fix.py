"""
Script to apply the fix to the vector_search_tenant_docs API endpoint.

This script modifies the vector_search_tenant_docs function in src/api/v1/endpoints/query.py
to correctly handle the filters parameter and return the proper response format.
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
    """Apply the fix to the vector_search_tenant_docs API endpoint."""
    try:
        # Path to the query.py file
        query_py_path = Path("src/api/v1/endpoints/query.py")
        
        # Check if the file exists
        if not query_py_path.exists():
            logger.error(f"File not found: {query_py_path}")
            return False
        
        # Read the file content
        with open(query_py_path, "r") as f:
            content = f.read()
        
        # Find the vector_search_tenant_docs function
        pattern = r'@router\.post\("/vector-search-tenant-docs"\)\nasync def vector_search_tenant_docs\(.*?return response.*?except Exception as e:.*?from e'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.error("Could not find the vector_search_tenant_docs function in the file")
            return False
        
        # The original function code
        original_function = match.group(0)
        
        # The fixed function code
        fixed_function = '''@router.post("/vector-search-tenant-docs")
async def vector_search_tenant_docs(
    request: VectorSearchTenantDocsRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    weaviate_client: Annotated[WeaviateClient, Depends(get_weaviate_client)],
):
    """
    Semantically search tenant-specific uploaded files, filtered by organization_id, to retrieve relevant documents.
    
    This endpoint simulates the Vector Search Docs node in SynthDrive's LangGraph system. It performs a semantic search
    in Weaviate's Tenant_UploadedFiles collection, filtered by organization_id, and returns the matching documents.
    
    Example query: "financial reports from 2023"
    """
    logger.info(f"Processing Vector Search Tenant Docs query: {request.query} for organization: {request.organization_id}")
    
    try:
        # Initialize the Vector Search Tenant Docs node
        vector_search_tenant_docs_node = VectorSearchTenantDocsNode(weaviate_client=weaviate_client)
        
        # Create the initial state
        initial_state = {
            "original_query": request.query,
            "organization_id": request.organization_id,
            "plan": None,
            "retrieved_docs": [],
            "graph_insights": [],
            "final_answer": None,
            "error_log": []
        }
        
        # Search for tenant documents using the Vector Search Tenant Docs node
        result_state = await vector_search_tenant_docs_node.search_tenant_documents(initial_state)
        
        # Check for errors
        if result_state.get("error_log") and len(result_state["error_log"]) > 0:
            error_message = result_state["error_log"][-1]
            logger.error(f"Error in Vector Search Tenant Docs: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search for tenant documents: {error_message}",
            )
        
        # Apply additional filters if provided
        filtered_docs = result_state.get("retrieved_docs", [])
        
        if request.filters:
            # Apply file_type filter
            if "file_type" in request.filters:
                filtered_docs = [doc for doc in filtered_docs if doc.get("file_type") == request.filters["file_type"]]
            
            # Apply tags filter
            if "tags" in request.filters and request.filters["tags"]:
                filtered_docs = [
                    doc for doc in filtered_docs 
                    if doc.get("tags") and all(tag in doc.get("tags", []) for tag in request.filters["tags"])
                ]
        
        # Limit the number of results
        filtered_docs = filtered_docs[:request.limit]
        
        # Convert the retrieved documents to TenantUploadedFile objects
        files = []
        for doc in filtered_docs:
            files.append(TenantUploadedFile(
                file_id=doc.get("file_id", ""),
                file_name=doc.get("file_name", "Unknown File"),
                file_path=doc.get("file_path", ""),
                content_chunk=doc.get("content", ""),  # Map content back to content_chunk
                organization_id=doc.get("organization_id", ""),
                upload_date=doc.get("upload_date", ""),
                file_type=doc.get("file_type", ""),
                tags=doc.get("tags", []),
                relevance_score=doc.get("relevance_score", 0.0),
                citation_id=doc.get("citation_id", "")
            ))
        
        # Create and return the response
        response = VectorSearchTenantDocsResponse(
            query=request.query,
            organization_id=request.organization_id,
            files=files
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Vector Search Tenant Docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search for tenant documents: {str(e)}",
        ) from e'''
        
        # Replace the original function with the fixed function
        new_content = content.replace(original_function, fixed_function)
        
        # Create a backup of the original file
        backup_path = query_py_path.with_suffix(".py.bak")
        with open(backup_path, "w") as f:
            f.write(content)
        logger.info(f"Created backup of original file at {backup_path}")
        
        # Write the modified content back to the file
        with open(query_py_path, "w") as f:
            f.write(new_content)
        
        logger.info(f"Successfully applied fix to {query_py_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error applying fix: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Applying fix to vector_search_tenant_docs API endpoint...")
    success = apply_fix()
    if success:
        logger.info("Fix applied successfully!")
    else:
        logger.error("Failed to apply fix")