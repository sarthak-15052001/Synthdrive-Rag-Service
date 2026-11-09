"""
Tenant Files Prompt Template Module

This module provides prompt templates for the tenant uploaded files search functionality.
These templates guide the LLM in handling tenant-specific corporate intelligence with
proper security boundaries and citation.
"""

from typing import Dict, Any, List, Optional

# Base prompt template for tenant uploaded files search
TENANT_FILES_PROMPT_TEMPLATE = """
You are handling the SynthDrive Tenant Knowledge Domain for Uploaded Corporate Intelligence.

CONTEXT:
- Files are stored raw in GCS for citations, and content chunks embedded in Weaviate for semantic search
- All content is isolated by organization_id to ensure confidentiality and prevent cross-tenant access
- You must always cite the original file path when providing information from tenant files
- You must never share information from one organization with another organization
- You must maintain strict confidentiality of all corporate intelligence

For the query: {query}

I have searched and found the following relevant content from the organization's uploaded files:

{search_results}

INSTRUCTIONS:
1. Provide a comprehensive answer based ONLY on the information in these file chunks
2. Cite the source files for each piece of information using the format [file_name]
3. If the information needed is not in the provided chunks, clearly state that it's not available
4. Do not make up or infer information that is not explicitly stated in the provided chunks
5. Maintain strict confidentiality and do not reference information from other organizations
6. If the query appears to be asking for information from another organization, politely explain that you can only access information from the current organization

Your response should be well-structured, informative, and properly cited.
"""

# Function to format search results for the prompt
def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results for inclusion in the prompt template.
    
    Args:
        results: List of search results from tenant uploaded files
        
    Returns:
        Formatted string of search results
    """
    if not results:
        return "No relevant files found for this query."
    
    formatted_results = []
    
    for i, result in enumerate(results):
        file_name = result.get("file_name", "Unknown File")
        file_path = result.get("file_path", "")
        content = result.get("content_chunk", "")
        relevance = result.get("relevance_score", 0.0)
        
        formatted_result = f"FILE CHUNK {i+1} [Relevance: {relevance:.2f}]\n"
        formatted_result += f"Source: {file_name}\n"
        formatted_result += f"Path: {file_path}\n"
        formatted_result += f"Content:\n{content}\n\n"
        
        formatted_results.append(formatted_result)
    
    return "\n".join(formatted_results)

# Function to generate the complete prompt
def generate_tenant_files_prompt(query: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Generate the complete prompt for tenant files search.
    
    Args:
        query: The user's query
        search_results: List of search results from tenant uploaded files
        
    Returns:
        Complete prompt for the LLM
    """
    formatted_results = format_search_results(search_results)
    
    prompt = TENANT_FILES_PROMPT_TEMPLATE.format(
        query=query,
        search_results=formatted_results
    )
    
    return prompt

# Enhanced prompt template with additional security checks
ENHANCED_TENANT_FILES_PROMPT_TEMPLATE = """
You are handling the SynthDrive Tenant Knowledge Domain for Uploaded Corporate Intelligence.

SECURITY CONTEXT:
- Files are stored raw in GCS for citations, and content chunks embedded in Weaviate for semantic search
- All content is isolated by organization_id ({organization_id}) to ensure confidentiality
- You must NEVER share information from one organization with another organization
- You must maintain strict confidentiality of all corporate intelligence
- You must ONLY use information from the provided file chunks

For the query: {query}

I have searched and found the following relevant content from organization {organization_id}'s uploaded files:

{search_results}

INSTRUCTIONS:
1. Provide a comprehensive answer based ONLY on the information in these file chunks
2. Cite the source files for each piece of information using the format [file_name]
3. If the information needed is not in the provided chunks, clearly state that it's not available
4. Do not make up or infer information that is not explicitly stated in the provided chunks
5. Maintain strict confidentiality and do not reference information from other organizations
6. If the query appears to be asking for information from another organization, politely explain that you can only access information from organization {organization_id}
7. Include relevant quotes from the documents to support your answer, always with proper citation

Your response should be well-structured, informative, and properly cited.
"""

# Function to generate the enhanced prompt
def generate_enhanced_tenant_files_prompt(
    query: str, 
    search_results: List[Dict[str, Any]], 
    organization_id: str
) -> str:
    """
    Generate the enhanced prompt for tenant files search with additional security context.
    
    Args:
        query: The user's query
        search_results: List of search results from tenant uploaded files
        organization_id: The organization ID for isolation
        
    Returns:
        Complete enhanced prompt for the LLM
    """
    formatted_results = format_search_results(search_results)
    
    prompt = ENHANCED_TENANT_FILES_PROMPT_TEMPLATE.format(
        query=query,
        search_results=formatted_results,
        organization_id=organization_id
    )
    
    return prompt