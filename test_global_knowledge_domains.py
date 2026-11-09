import requests
import json
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL
BASE_URL = "http://localhost:8000"

# Authentication token (replace with your actual token)
# No authentication for testing
AUTH_TOKEN = None
HEADERS = {
    "Content-Type": "application/json"
}


def ingest_global_tool(tool_data: Dict[str, Any]) -> str:
    """
    Ingest an AI tool into the global knowledge domain.
    
    Args:
        tool_data: Dictionary containing tool data
        
    Returns:
        Job ID for the ingestion process
    """
    url = f"{BASE_URL}/api/v1/rag/ingest/global/tool"
    response = requests.post(url, json=tool_data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        job_id = result.get("job_id")
        logger.info(f"Successfully started ingestion of AI tool with job ID: {job_id}")
        return job_id
    else:
        logger.error(f"Failed to ingest AI tool: {response.text}")
        response.raise_for_status()

def ingest_global_learning_resource(resource_data: Dict[str, Any]) -> str:
    """
    Ingest a learning resource into the global knowledge domain.
    
    Args:
        resource_data: Dictionary containing learning resource data
        
    Returns:
        Job ID for the ingestion process
    """
    url = f"{BASE_URL}/api/v1/rag/ingest/global/learning-resource"
    response = requests.post(url, json=resource_data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        job_id = result.get("job_id")
        logger.info(f"Successfully started ingestion of learning resource with job ID: {job_id}")
        return job_id
    else:
        logger.error(f"Failed to ingest learning resource: {response.text}")
        response.raise_for_status()

def ingest_global_ecosystem_partner(partner_data: Dict[str, Any]) -> str:
    """
    Ingest an ecosystem partner into the global knowledge domain.
    
    Args:
        partner_data: Dictionary containing ecosystem partner data
        
    Returns:
        Job ID for the ingestion process
    """
    url = f"{BASE_URL}/api/v1/rag/ingest/global/ecosystem-partner"
    response = requests.post(url, json=partner_data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        job_id = result.get("job_id")
        logger.info(f"Successfully started ingestion of ecosystem partner with job ID: {job_id}")
        return job_id
    else:
        logger.error(f"Failed to ingest ecosystem partner: {response.text}")
        response.raise_for_status()

def search_ai_tools(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for AI tools in the global knowledge domain.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    url = f"{BASE_URL}/api/v1/rag/tools/search"
    data = {
        "query": query,
        "limit": limit,
        "tenant_id": "global"
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Successfully searched for AI tools with query: {query}")
        return result
    else:
        logger.error(f"Failed to search for AI tools: {response.text}")
        response.raise_for_status()

def search_learning_resources(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for learning resources in the global knowledge domain.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    url = f"{BASE_URL}/api/v1/rag/learning-resources/search"
    data = {
        "query": query,
        "limit": limit,
        "tenant_id": "global"
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Successfully searched for learning resources with query: {query}")
        return result
    else:
        logger.error(f"Failed to search for learning resources: {response.text}")
        response.raise_for_status()

def search_ecosystem_partners(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for ecosystem partners in the global knowledge domain.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    url = f"{BASE_URL}/api/v1/rag/ecosystem-partners/search"
    data = {
        "query": query,
        "limit": limit,
        "tenant_id": "global"
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Successfully searched for ecosystem partners with query: {query}")
        return result
    else:
        logger.error(f"Failed to search for ecosystem partners: {response.text}")
        response.raise_for_status()

def main():
    """Main function to test the global knowledge domain endpoints."""
    try:
        # Test ingesting an AI tool
        tool_data = {
            "name": "GPT-4 Turbo",
            "description": "Advanced language model with improved capabilities for text generation and understanding.",
            "use_case": "Content creation, code generation, conversational AI, and data analysis.",
            "url": "https://openai.com/gpt-4",
            "category": "Language Model",
            "pricing": "Subscription-based",
            "reviews": "Highly rated for its accuracy and versatility.",
            "rating": 4.8,
            "tags": ["AI", "NLP", "Machine Learning"]
        }
        
        tool_job_id = ingest_global_tool(tool_data)
        logger.info(f"AI tool ingestion job ID: {tool_job_id}")
        
        # Test ingesting a learning resource
        resource_data = {
            "title": "Fine-tuning LLMs: A Comprehensive Guide",
            "content": """
            # Fine-tuning Large Language Models
            
            This guide covers the essential techniques for fine-tuning large language models like GPT-4.
            
            ## Introduction
            
            Fine-tuning allows you to adapt pre-trained models to specific tasks or domains.
            
            ## Key Techniques
            
            1. **Data Preparation**: Curate high-quality training examples.
            2. **Hyperparameter Selection**: Choose appropriate learning rates and batch sizes.
            3. **Evaluation**: Use appropriate metrics to assess model performance.
            
            ## Best Practices
            
            - Start with a small dataset to validate your approach.
            - Use a validation set to prevent overfitting.
            - Consider using techniques like LoRA for parameter-efficient fine-tuning.
            """,
            "url": "https://example.com/llm-fine-tuning-guide",
            "author": "AI Research Team",
            "resource_type": "tutorial",
            "tags": ["LLM", "Fine-tuning", "NLP", "Machine Learning"]
        }
        
        resource_job_id = ingest_global_learning_resource(resource_data)
        logger.info(f"Learning resource ingestion job ID: {resource_job_id}")
        
        # Test ingesting an ecosystem partner
        partner_data = {
            "name": "AI Solutions Inc.",
            "bio": "Leading provider of enterprise AI solutions with expertise in custom LLM deployment and integration.",
            "expertise": ["LLM Integration", "Enterprise AI", "Custom Model Development"],
            "certifications": ["OpenAI Certified Partner", "Google Cloud AI Partner"],
            "case_studies": "Successfully deployed custom RAG solutions for Fortune 500 companies in finance and healthcare sectors.",
            "website": "https://example.com/ai-solutions",
            "contact_info": "contact@example.com",
            "budget_tier": "enterprise",
            "tags": ["Enterprise", "Integration", "Consulting"]
        }
        
        partner_job_id = ingest_global_ecosystem_partner(partner_data)
        logger.info(f"Ecosystem partner ingestion job ID: {partner_job_id}")
        
        # Wait for ingestion to complete
        logger.info("Waiting for ingestion to complete (10 seconds)...")
        time.sleep(10)
        
        # Test searching for AI tools
        ai_tools_results = search_ai_tools("language model for content creation")
        logger.info(f"AI Tools search results: {json.dumps(ai_tools_results, indent=2)}")
        
        # Test searching for learning resources
        learning_resources_results = search_learning_resources("fine-tuning language models")
        logger.info(f"Learning Resources search results: {json.dumps(learning_resources_results, indent=2)}")
        
        # Test searching for ecosystem partners
        ecosystem_partners_results = search_ecosystem_partners("enterprise AI solutions")
        logger.info(f"Ecosystem Partners search results: {json.dumps(ecosystem_partners_results, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")

if __name__ == "__main__":
    main()