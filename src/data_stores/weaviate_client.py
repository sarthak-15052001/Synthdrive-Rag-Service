
import weaviate
from weaviate.auth import AuthApiKey
from typing import Dict, List, Any, Optional, Union
from openai import OpenAI
import uuid
import logging

# Try to import LangChain components, but make them optional
try:
    from langchain_community.vectorstores import Weaviate as LangChainWeaviate
    from langchain_openai import OpenAIEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logging.warning("LangChain components not available. Some features will be disabled.")
    LANGCHAIN_AVAILABLE = False

from src.core.config import settings


class WeaviateClient:
    """
    Client for interacting with Weaviate vector database.
    Provides integration with LangChain's Weaviate vector store.
    """

    def __init__(self, weaviate_url: Optional[str] = None, api_key: Optional[str] = None):
        # Store URL and API key as instance variables
        self.weaviate_url = weaviate_url or settings.WEAVIATE_URL
        self.api_key = api_key or settings.WEAVIATE_API_KEY
        
        # Initialize OpenAI client for embeddings with proper configuration
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
        }
        
        # Add organization if available
        if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
            client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
            
        self.openai_client = OpenAI(**client_kwargs)
        
        # Initialize Weaviate client
        self.client = self._init_client()
        
        try:
            # Create schema if it doesn't exist
            self._ensure_schema()
            
            # Create schema classes
            self.create_classes()
        except Exception as e:
            logging.error(f"Error initializing Weaviate schema: {str(e)}")
            raise
        
        # Initialize LangChain components if available
        if LANGCHAIN_AVAILABLE:
            # Initialize LangChain embeddings
            self.embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Initialize LangChain Weaviate vector store
            self.vector_store = LangChainWeaviate(
                client=self.client,
                index_name="Document",
                text_key="content",
                embedding=self.embeddings,
                by_text=False
            )
        else:
            self.embeddings = None
            self.vector_store = None
    def create_classes(self):
            """Create Weaviate classes if they don't exist."""
            try:
                # Try to get the schema
                logging.info("Retrieving Weaviate schema...")
                schema = self.client.schema.get()
                
                # Check which classes exist
                existing_classes = []
                if schema and "classes" in schema:
                    existing_classes = [cls.get("class") for cls in schema["classes"]]
                    logging.info(f"Found existing classes: {', '.join(existing_classes)}")
                else:
                    logging.info("No existing classes found in schema")
                
                # Create Global_Tools class if it doesn't exist
                if "Global_Tools" not in existing_classes:
                    logging.info("Creating Global_Tools class...")
                    self._create_global_tools_class()
                
                # Create Global_LearningResources class if it doesn't exist
                if "Global_LearningResources" not in existing_classes:
                    logging.info("Creating Global_LearningResources class...")
                    self._create_global_learning_resources_class()
                
                # Create Global_Ecosystem class if it doesn't exist
                if "Global_Ecosystem" not in existing_classes:
                    logging.info("Creating Global_Ecosystem class...")
                    self._create_global_ecosystem_class()
                
                # Create Tenant_UploadedFiles class if it doesn't exist
                if "Tenant_UploadedFiles" not in existing_classes:
                    logging.info("Creating Tenant_UploadedFiles class...")
                    self._create_tenant_uploaded_files_class()
                
                # Create NoCodeTemplates class if it doesn't exist
                if "NoCodeTemplates" not in existing_classes:
                    logging.info("Creating NoCodeTemplates class...")
                    self._create_no_code_templates_class()
                
                # Create Pre_Made_Prompts class if it doesn't exist
                if "Pre_Made_Prompts" not in existing_classes:
                    logging.info("Creating Pre_Made_Prompts class...")
                    self._create_pre_made_prompts_class()
                    
                logging.info("All required Weaviate classes have been created or already exist")
                    
            except Exception as e:
                logging.error(f"Error checking or creating schema: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
                raise
    
    def _create_global_tools_class(self):
        """Create the Global_Tools class in Weaviate."""
        try:
            class_obj = {
                "class": "Global_Tools",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "name",
                        "dataType": ["string"],
                        "description": "Name of the AI tool"
                    },
                    {
                        "name": "homepage_url",
                        "dataType": ["string"],
                        "description": "Homepage URL of the tool"
                    },
                    {
                        "name": "last_scraped_at",
                        "dataType": ["date"],
                        "description": "When the tool was last scraped"
                    },
                    {
                        "name": "source_urls",
                        "dataType": ["string[]"],
                        "description": "Source URLs for the tool"
                    },
                    {
                        "name": "categories_json",
                        "dataType": ["text"],
                        "description": "Categories as JSON string with primary and secondary"
                    },
                    {
                        "name": "short_description",
                        "dataType": ["text"],
                        "description": "Brief description of the tool"
                    },
                    {
                        "name": "detailed_description",
                        "dataType": ["text"],
                        "description": "Detailed description of the tool"
                    },
                    {
                        "name": "features_json",
                        "dataType": ["text"],
                        "description": "Features as JSON string (array of {name, description, use_case})"
                    },
                    {
                        "name": "differentiators",
                        "dataType": ["text[]"],
                        "description": "Unique selling points of the tool"
                    },
                    {
                        "name": "subscriptions_json",
                        "dataType": ["text"],
                        "description": "Subscriptions as JSON string (array of subscription objects)"
                    },
                    {
                        "name": "compliance_json",
                        "dataType": ["text"],
                        "description": "Compliance data as JSON string"
                    },
                    {
                        "name": "documentation_links",
                        "dataType": ["string[]"],
                        "description": "Links to documentation"
                    },
                    {
                        "name": "rating",
                        "dataType": ["number"],
                        "description": "Rating of the tool"
                    },
                    {
                        "name": "logo_url",
                        "dataType": ["string"],
                        "description": "URL of the tool's logo"
                    },
                    {
                        "name": "tags",
                        "dataType": ["string[]"],
                        "description": "Tags associated with the tool"
                    },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Combined content for embedding"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: Global_Tools")
        except Exception as e:
            logging.error(f"Error creating Global_Tools class: {str(e)}")
    
    def _create_global_learning_resources_class(self):
        """Create the Global_LearningResources class in Weaviate with JSON support for nested structures."""
        try:
            class_obj = {
                "class": "Global_LearningResources",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "title",
                        "dataType": ["string"],
                        "description": "Title of the learning resource"
                    },
                    {
                        "name": "description",
                        "dataType": ["text"],
                        "description": "Description of the learning resource"
                    },
                    {
                        "name": "source_url",
                        "dataType": ["string"],
                        "description": "Source URL of the learning resource"
                    },
                    {
                        "name": "resource_type",
                        "dataType": ["string"],
                        "description": "Type of learning resource (course, tutorial, article, etc.)"
                    },
                    {
                        "name": "categories_json",
                        "dataType": ["text"],
                        "description": "Categories as JSON string with primary and secondary"
                    },
                    {
                        "name": "topics_discussed",
                        "dataType": ["string[]"],
                        "description": "Topics discussed in the resource"
                    },
                    {
                        "name": "target_audience_json",
                        "dataType": ["text"],
                        "description": "Target audience as JSON string with expertise_level and job_roles"
                    },
                    {
                        "name": "useful_context",
                        "dataType": ["string[]"],
                        "description": "Useful contexts for the resource"
                    },
                    {
                        "name": "content_json",
                        "dataType": ["text"],
                        "description": "Content as JSON string with summary, learning_objectives, full_text_markdown, video_transcript, and video_url"
                    },
                    {
                        "name": "tags",
                        "dataType": ["string[]"],
                        "description": "Tags associated with the resource"
                    },
                    {
                        "name": "estimatedTime",
                        "dataType": ["string"],
                        "description": "Estimated time to consume the resource"
                    },
                    {
                        "name": "platform_name",
                        "dataType": ["string"],
                        "description": "Platform name (e.g., Coursera, Udemy)"
                    },
                    {
                        "name": "platform_logo_url",
                        "dataType": ["string"],
                        "description": "Platform logo URL"
                    },
                    {
                        "name": "associated_tool",
                        "dataType": ["string"],
                        "description": "Associated tool (e.g., ChatGPT, Claude)"
                    },
                    {
                        "name": "taxonomy_json",
                        "dataType": ["text"],
                        "description": "Taxonomy as JSON string (department, team_task_category, type_category)"
                    },
                    {
                        "name": "kpi_benefits_json",
                        "dataType": ["text"],
                        "description": "KPI benefits as JSON string (estimated_time_saving, efficiency_gain_percentage, cost_reduction, quality_improvement_metric)"
                    },
                    {
                        "name": "is_paid",
                        "dataType": ["boolean"],
                        "description": "Whether the resource is paid or free"
                    },
                    {
                        "name": "subscriptions_json",
                        "dataType": ["text"],
                        "description": "Subscriptions as JSON string (plan_name, price_monthly, price_annual, pricing_model, features_included)"
                    },
                    {
                        "name": "resource_id",
                        "dataType": ["string"],
                        "description": "Unique identifier for the resource"
                    },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: Global_LearningResources with JSON support for nested structures and comprehensive fields")
        except Exception as e:
            logging.error(f"Error creating Global_LearningResources class: {str(e)}")
    
    def _create_global_ecosystem_class(self):
        """Create the Global_Ecosystem class in Weaviate."""
        try:
            class_obj = {
                "class": "Global_Ecosystem",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "name",
                        "dataType": ["string"],
                        "description": "Name of the ecosystem partner"
                    },
                    {
                        "name": "bio",
                        "dataType": ["text"],
                        "description": "Biography or description of the partner"
                    },
                    {
                        "name": "expertise",
                        "dataType": ["string[]"],
                        "description": "Areas of expertise"
                    },
                    {
                        "name": "certifications",
                        "dataType": ["string[]"],
                        "description": "Certifications held by the partner"
                    },
                    {
                        "name": "case_studies",
                        "dataType": ["text"],
                        "description": "Case studies or success stories"
                    },
                    {
                        "name": "website",
                        "dataType": ["string"],
                        "description": "Partner's website"
                    },
                    {
                        "name": "contact_info",
                        "dataType": ["string"],
                        "description": "Contact information"
                    },
                    {
                        "name": "budget_tier",
                        "dataType": ["string"],
                        "description": "Budget tier (enterprise, mid-market, etc.)"
                    },
                    {
                        "name": "partner_id",
                        "dataType": ["string"],
                        "description": "Unique identifier for the partner"
                    },
                    {
                        "name": "tags",
                        "dataType": ["string[]"],
                        "description": "Tags associated with the partner"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Combined content for embedding"
                    },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: Global_Ecosystem")
        except Exception as e:
            logging.error(f"Error creating Global_Ecosystem class: {str(e)}")
            
    def _create_tenant_uploaded_files_class(self):
        """Create the Tenant_UploadedFiles class in Weaviate."""
        try:
            class_obj = {
                "class": "Tenant_UploadedFiles",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "file_name",
                        "dataType": ["string"],
                        "description": "Name of the uploaded file"
                    },
                    {
                        "name": "file_path",
                        "dataType": ["string"],
                        "description": "Path to the file in storage (e.g., GCS bucket)"
                    },
                    {
                        "name": "content_chunk",
                        "dataType": ["text"],
                        "description": "Content chunk from the file"
                    },
                    {
                        "name": "organization_id",
                        "dataType": ["string"],
                        "description": "Organization ID that owns this file"
                    },
                    {
                        "name": "upload_date",
                        "dataType": ["date"],
                        "description": "When the file was uploaded"
                    },
                    {
                        "name": "file_type",
                        "dataType": ["string"],
                        "description": "Type of file (PDF, DOCX, etc.)"
                    },
                    {
                        "name": "file_id",
                        "dataType": ["string"],
                        "description": "Unique identifier for the file"
                    },
                    {
                        "name": "tags",
                        "dataType": ["string[]"],
                        "description": "Tags associated with the file"
                    },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: Tenant_UploadedFiles")
        except Exception as e:
            logging.error(f"Error creating Tenant_UploadedFiles class: {str(e)}")
    
    def _create_no_code_templates_class(self):
        """Create the NoCodeTemplates class in Weaviate."""
        try:
            class_obj = {
                "class": "NoCodeTemplates",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "name",
                        "dataType": ["string"],
                        "description": "Name of the no-code template"
                    },
                    {
                        "name": "source_url",
                        "dataType": ["string"],
                        "description": "Source URL of the template"
                    },
                    {
                        "name": "platform",
                        "dataType": ["string"],
                        "description": "Platform the template is for (e.g., n8n, Zapier, Make)"
                    },
                    {
                        "name": "platform_logo_url",
                        "dataType": ["string"],
                        "description": "Logo URL of the platform"
                    },
                    {
                        "name": "use_cases",
                        "dataType": ["string[]"],
                        "description": "Use cases for the template"
                    },
                    {
                        "name": "short_description",
                        "dataType": ["text"],
                        "description": "Short description of the template"
                    },
                    {
                        "name": "complexity",
                        "dataType": ["string"],
                        "description": "Complexity level (e.g., beginner, intermediate, advanced)"
                    },
                    {
                        "name": "categories_json",
                        "dataType": ["text"],
                        "description": "Categories as JSON string with primary and secondary"
                    },
                    {
                        "name": "concrete_tasks",
                        "dataType": ["string[]"],
                        "description": "Concrete tasks that can be accomplished with this template"
                    },
                    {
                        "name": "required_connections",
                        "dataType": ["string[]"],
                        "description": "Required connections/integrations for the template"
                    },
                    {
                        "name": "taxonomy_json",
                        "dataType": ["text"],
                        "description": "Taxonomy as JSON string (department, team_task_category, type_category)"
                    },
                    {
                        "name": "target_audience_json",
                        "dataType": ["text"],
                        "description": "Target audience as JSON string (expertise_level, job_roles)"
                    },
                    {
                        "name": "kpi_benefits_json",
                        "dataType": ["text"],
                        "description": "KPI benefits as JSON string (estimated_time_saving, efficiency_gain_percentage, cost_reduction, quality_improvement_metric)"
                    },
                    {
                        "name": "blueprint_json_url",
                        "dataType": ["string"],
                        "description": "URL to the blueprint JSON file"
                    },
                    {
                        "name": "uuid",
                        "dataType": ["string"],
                        "description": "Unique identifier for the template"
                    },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Combined content for embedding"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: NoCodeTemplates")
        except Exception as e:
            logging.error(f"Error creating NoCodeTemplates class: {str(e)}")
    
    def _create_pre_made_prompts_class(self):
        """Create the Pre_Made_Prompts class in Weaviate."""
        try:
            class_obj = {
                "class": "Pre_Made_Prompts",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "name",
                        "dataType": ["string"],
                        "description": "Name of the pre-made prompt"
                    },
                    {
                        "name": "prompt_body",
                        "dataType": ["text"],
                        "description": "The actual prompt text with placeholders"
                    },
                    {
                        "name": "placeholders",
                        "dataType": ["string[]"],
                        "description": "List of placeholder variables in the prompt"
                    },
                    {
                        "name": "associated_tool",
                        "dataType": ["string"],
                        "description": "The tool this prompt is designed for (e.g., Perplexity, Claude)"
                    },
                    {
                        "name": "concrete_tasks",
                        "dataType": ["string[]"],
                        "description": "Specific tasks this prompt can accomplish"
                    },
                    {
                        "name": "taxonomy_json",
                        "dataType": ["text"],
                        "description": "Taxonomy data as JSON string (primary_category, secondary_categories, department, team)"
                    },
                    {
                        "name": "target_audience_json",
                        "dataType": ["text"],
                        "description": "Target audience as JSON string (expertise_level, job_roles)"
                    },
                    {
                        "name": "kpi_benefits_json",
                        "dataType": ["text"],
                        "description": "KPI benefits as JSON string (kpi_name, expected_improvement, etc.)"
                    },
                    {
                        "name": "model_compatibility",
                        "dataType": ["string[]"],
                        "description": "List of AI models compatible with this prompt"
                    },
                    {
                        "name": "prompting_technique",
                        "dataType": ["string"],
                        "description": "The prompting technique used (e.g., Chain-of-thought, Few-shot)"
                    },
                    {
                        "name": "tags",
                        "dataType": ["string[]"],
                        "description": "Tags associated with the prompt"
                    },
                    # {
                    #     "name": "prompt_id",
                    #     "dataType": ["string"],
                    #     "description": "Unique identifier for the prompt"
                    # },
                    {
                        "name": "tenant_id",
                        "dataType": ["string"],
                        "description": "Tenant ID"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Combined content for embedding"
                    }
                ]
            }
            
            self.client.schema.create_class(class_obj)
            logging.info("Created Weaviate class: Pre_Made_Prompts")
        except Exception as e:
            logging.error(f"Error creating Pre_Made_Prompts class: {str(e)}")
            
    def _init_client(self):
        """
        Initialize the Weaviate client with authentication.
        """
        try:
            # Check if this is a local instance (no authentication needed)
            is_local = "localhost" in self.weaviate_url or "127.0.0.1" in self.weaviate_url
            
            # Set a longer timeout (in seconds)
            timeout_config = 600.0  # 10 minutes timeout
            
            if is_local:
                # For local instances with anonymous access enabled
                logging.info(f"Connecting to local Weaviate instance at {self.weaviate_url}")
                return weaviate.Client(
                    url=self.weaviate_url,
                    additional_headers={
                        "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
                    },
                    timeout_config=timeout_config
                )
            else:
                # For remote instances with API key authentication
                logging.info(f"Connecting to remote Weaviate instance at {self.weaviate_url}")
                if not self.api_key:
                    logging.warning("No API key provided for remote Weaviate instance. Using API key from settings.")
                    
                auth_config = AuthApiKey(api_key=self.api_key) if self.api_key else None
                
                # Add retry logic for connection issues
                max_retries = 3
                retry_delay = 2  # seconds
                
                # Set a longer timeout (in seconds)
                timeout_config = 600.0  # 10 minutes timeout
                
                for attempt in range(max_retries):
                    try:
                        client = weaviate.Client(
                            url=self.weaviate_url,
                            auth_client_secret=auth_config,
                            additional_headers={
                                "X-OpenAI-Api-Key": settings.OPENAI_API_KEY
                            },
                            timeout_config=timeout_config
                        )
                        
                        # Test the connection by getting the schema
                        client.schema.get()
                        logging.info(f"Successfully connected to Weaviate on attempt {attempt + 1}")
                        return client
                    except Exception as retry_error:
                        if attempt < max_retries - 1:
                            logging.warning(f"Connection attempt {attempt + 1} failed: {str(retry_error)}. Retrying in {retry_delay} seconds...")
                            import time
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logging.error(f"Failed to connect to Weaviate after {max_retries} attempts: {str(retry_error)}")
                            raise
        except Exception as e:
            logging.error(f"Failed to initialize Weaviate client: {str(e)}")
            raise

    def _ensure_schema(self):
        """
        Ensure that the required schema exists in Weaviate.
        """
        # Only create the Document class if it doesn't exist
        if not self.client.schema.exists("Document"):
            # Define the Document class
            document_class = {
                "class": "Document",
                "description": "A document in the RAG system",
                "vectorizer": "text2vec-openai",  # Use OpenAI for vectorization
                "moduleConfig": {
                    "text2vec-openai": {
                        "model": "ada",  # Weaviate v3 uses simple model names
                        "modelVersion": "002",
                        "type": "text"
                    }
                },
                "properties": [
                    {
                        "name": "content",
                        "description": "The content of the document",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": False,
                                "vectorizePropertyName": False
                            }
                        }
                    },
                    {
                        "name": "metadata",
                        "description": "Metadata about the document (JSON string containing all metadata fields)",
                        "dataType": ["text"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True
                            }
                        }
                    },
                    {
                        "name": "tenant_id",
                        "description": "ID of the tenant that owns this document",
                        "dataType": ["string"],
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True
                            }
                        }
                    }
                ]
            }
            
            # Create the class
            self.client.schema.create_class(document_class)

    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for the given text using OpenAI.
        
        Args:
            text: The text to create an embedding for
            
        Returns:
            The embedding vector
        """
        try:
            # Ensure text is not empty
            if not text or len(text.strip()) == 0:
                logging.warning("Empty text provided for embedding, using placeholder")
                text = "empty document"
                
            # Truncate text if it's too long (OpenAI has token limits)
            if len(text) > 8000:
                logging.warning(f"Text too long ({len(text)} chars), truncating to 8000 chars")
                text = text[:8000]
                
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Error creating embedding: {str(e)}")
            # Return a zero vector as fallback (1536 is the dimension of OpenAI embeddings)
            return [0.0] * 1536

    def upsert_vector(self, doc_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]) -> str:
        """
        Upsert a document vector into Weaviate.
        
        Args:
            doc_id: The ID of the document
            content: The content of the document
            embedding: The embedding vector for the content
            metadata: Metadata about the document
            
        Returns:
            The ID of the created/updated document
        """
        # Ensure doc_id is a valid UUID
        try:
            # Try to parse as UUID
            uuid_obj = uuid.UUID(doc_id)
            doc_id = str(uuid_obj)
        except (ValueError, AttributeError, TypeError):
            # If not a valid UUID, generate a new one
            doc_id = str(uuid.uuid4())
            logging.info(f"Generated new UUID: {doc_id}")
        
        # Create properties for the document
        import json as json_lib
        
        # Extract tenant_id for top-level filtering
        tenant_id = metadata.get("tenant_id", "default")
        
        # Create a copy of metadata WITHOUT tenant_id to avoid duplication
        # (tenant_id will be stored at top-level only)
        metadata_copy = metadata.copy()
        metadata_copy.pop("tenant_id", None)
        
        properties = {
            "content": content,
            "metadata": json_lib.dumps(metadata_copy),  # Metadata WITHOUT tenant_id
            "tenant_id": tenant_id  # Only at top level for filtering
        }
        
        # Upsert the document to Weaviate with the provided embedding
        try:
            # First try to create a new object
            result = self.client.data_object.create(
                class_name="Document",
                data_object=properties,
                uuid=doc_id,
                vector=embedding
            )
            return doc_id
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if "already exists" in str(e):
                # If the object already exists, update it
                self.client.data_object.update(
                    class_name="Document",
                    uuid=doc_id,
                    data_object=properties,
                    vector=embedding
                )
                return doc_id
            else:
                # Re-raise if it's a different error
                raise

    def semantic_search(self, query_embedding: List[float], tenant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search using the provided query embedding.
        Results are filtered by tenant_id.
        
        Args:
            query_embedding: The embedding vector for the query
            tenant_id: The tenant ID to filter results by
            limit: Maximum number of results to return
            
        Returns:
            List of documents matching the query
        """
        # Build the query with tenant_id filter
        query_builder = (
            self.client.query
            .get("Document", ["content", "metadata", "tenant_id", "_additional {certainty}"])
            .with_near_vector({"vector": query_embedding})
            .with_where({
                "path": ["tenant_id"],
                "operator": "Equal",
                "valueString": tenant_id
            })
            .with_limit(limit)
        )
        
        # Execute the query
        result = query_builder.do()
        
        # Process the results
        documents = []
        if result and "data" in result and "Get" in result["data"] and "Document" in result["data"]["Get"]:
            for doc in result["data"]["Get"]["Document"]:
                # Calculate relevance score from certainty
                certainty = doc["_additional"]["certainty"] if "_additional" in doc and "certainty" in doc["_additional"] else 0
                
                # Parse metadata if it's a JSON string
                import json
                metadata = doc.get("metadata", {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {"raw": metadata}
                
                documents.append({
                    "content": doc["content"],
                    "metadata": metadata,
                    "tenant_id": doc["tenant_id"],
                    "relevance_score": certainty
                })
        
        return documents

    def add_document(self, content: str, metadata: Dict[str, Any], embedding: List[float], class_name: str = "Document") -> str:
            """Add a document to Weaviate with optional class_name."""
            data_object = {
                "content": content,
                "tenant_id": metadata.get("tenant_id", "default")
            }
            
            # For tools, include all fields
            if class_name == "Global_Tools":
                # Ensure last_updated is in RFC3339 format
                last_updated = metadata.get("last_updated", "")
                if not last_updated:
                    from datetime import datetime, timezone
                    last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(last_updated, str) and "." in last_updated:
                    # If date has microseconds, convert to RFC3339 format
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                        last_updated = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        # If parsing fails, use current time
                        from datetime import datetime, timezone
                        last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                data_object.update({
                    "name": metadata.get("name", ""),
                    "description": metadata.get("description", ""),
                    "use_case": metadata.get("use_case", ""),
                    "reviews": metadata.get("reviews", ""),
                    "url": metadata.get("url", ""),
                    "pricing": metadata.get("pricing", ""),
                    "tool_id": metadata.get("tool_id", str(uuid.uuid4())),
                    "category": metadata.get("category", ""),
                    "tags": metadata.get("tags", []),
                    "rating": metadata.get("rating", 0.0),
                    "last_updated": last_updated
                })
            # For learning resources, include all fields
            elif class_name == "Global_LearningResources":
                # Ensure created_at is in RFC3339 format
                created_at = metadata.get("created_at", "")
                if not created_at:
                    from datetime import datetime, timezone
                    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(created_at, str) and "." in created_at:
                    # If date has microseconds, convert to RFC3339 format
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        # If parsing fails, use current time
                        from datetime import datetime, timezone
                        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                data_object.update({
                    "title": metadata.get("title", ""),
                    "url": metadata.get("url", ""),
                    "author": metadata.get("author", ""),
                    "resource_type": metadata.get("resource_type", ""),
                    "resource_id": metadata.get("resource_id", str(uuid.uuid4())),
                    "tags": metadata.get("tags", []),
                    "created_at": created_at
                })
            else:
                # For regular documents
                import json
                # Create a copy of metadata and remove tenant_id to avoid duplication
                # (tenant_id is already stored as a top-level field at line 979)
                metadata_copy = metadata.copy() if isinstance(metadata, dict) else metadata
                if isinstance(metadata_copy, dict):
                    metadata_copy.pop("tenant_id", None)  # Remove tenant_id from metadata JSON
                
                data_object.update({
                    "metadata": json.dumps(metadata_copy) if isinstance(metadata_copy, dict) else metadata_copy
                    # Note: tenant_id is stored as top-level field, not in metadata JSON
                })
            
            try:
                # Use a longer timeout for this specific operation
                import requests
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                
                # Create a session with retry logic and longer timeout
                session = requests.Session()
                retry_strategy = Retry(
                    total=5,
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
                    
                    # Execute the operation with longer timeout
                    obj_id = self.client.data_object.create(
                        data_object=data_object,
                        class_name=class_name,
                        vector=embedding
                    )
                finally:
                    # Restore the original session
                    self.client._connection._session = original_session
                
                logging.info(f"Added object to Weaviate class {class_name} with ID: {obj_id}")
                return obj_id
            except Exception as e:
                logging.error(f"Error adding document to Weaviate: {str(e)}")
                return str(uuid.uuid4())  # Return a fallback ID

    def query_documents(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5, class_name: str = "Document") -> List[Dict[str, Any]]:
            """Query documents in Weaviate with optional class_name."""
            near_text = {"concepts": [query]}
            
            # Define properties to retrieve based on class name
            if class_name == "Global_Tools":
                properties = [
                    "name", "homepage_url", "last_scraped_at", "source_urls",
                    "categories_json", "short_description", "detailed_description",
                    "features_json", "differentiators", "subscriptions_json",
                    "compliance_json", "documentation_links", "rating", "logo_url",
                    "tags", "tenant_id", "content"
                ]
            elif class_name == "Global_LearningResources":
                properties = [
                    "title", "description", "source_url", "resource_type",
                    "categories_json", "topics_discussed",
                    "target_audience_json", "useful_context",
                    "content_json", "tags",
                    "estimatedTime", "platform_name", "platform_logo_url",
                    "associated_tool", "taxonomy_json", "kpi_benefits_json",
                    "is_paid", "subscriptions_json",
                    "resource_id", "tenant_id"
                ]
            else:
                properties = ["content", "metadata", "tenant_id"]
            
            # Build and execute query
            try:
                query_builder = (
                    self.client.query
                    .get(class_name, properties)
                    .with_near_text(near_text)
                    .with_limit(limit)
                    .with_additional(["id", "certainty"])
                )
                
                # Add filters if provided
                if filters:
                    where_filter = self._build_where_filter(filters)
                    if where_filter:
                        query_builder = query_builder.with_where(where_filter)
                
                result = query_builder.do()
                
                # Process results
                documents = []
                for res in result.get("data", {}).get("Get", {}).get(class_name, []):
                    if class_name == "Global_Tools":
                        # Parse JSON fields to reconstruct the original payload structure
                        import json
                        
                        categories = json.loads(res.get("categories_json", "{}"))
                        features = json.loads(res.get("features_json", "[]"))
                        subscriptions = json.loads(res.get("subscriptions_json", "[]"))
                        compliance = json.loads(res.get("compliance_json", "{}"))
                        
                        documents.append({
                            "id": res["_additional"]["id"],
                            "name": res.get("name", ""),
                            "homepage_url": res.get("homepage_url", ""),
                            "last_scraped_at": res.get("last_scraped_at", ""),
                            "source_urls": res.get("source_urls", []),
                            "categories": categories,
                            "short_description": res.get("short_description", ""),
                            "detailed_description": res.get("detailed_description", ""),
                            "features": features,
                            "differentiators": res.get("differentiators", []),
                            "subscriptions": subscriptions,
                            "compliance": compliance,
                            "documentation_links": res.get("documentation_links", []),
                            "rating": res.get("rating", 0.0),
                            "logo_url": res.get("logo_url", ""),
                            "tags": res.get("tags", []),
                            "content": res.get("content", ""),
                            "tenant_id": res.get("tenant_id", "default"),
                            "relevance_score": res["_additional"]["certainty"]
                        })
                    elif class_name == "Global_LearningResources":
                        # Parse JSON fields to reconstruct the original payload structure
                        import json
                        
                        categories = json.loads(res.get("categories_json", "{}"))
                        target_audience = json.loads(res.get("target_audience_json", "{}"))
                        content = json.loads(res.get("content_json", "{}"))
                        taxonomy = json.loads(res.get("taxonomy_json", "null")) if res.get("taxonomy_json") else None
                        kpi_benefits = json.loads(res.get("kpi_benefits_json", "null")) if res.get("kpi_benefits_json") else None
                        subscriptions = json.loads(res.get("subscriptions_json", "null")) if res.get("subscriptions_json") else None
                        
                        documents.append({
                            "id": res["_additional"]["id"],
                            "resource_id": res.get("resource_id", ""),
                            "title": res.get("title", ""),
                            "description": res.get("description", ""),
                            "source_url": res.get("source_url", ""),
                            "resource_type": res.get("resource_type", ""),
                            "categories": categories,
                            "topics_discussed": res.get("topics_discussed", []),
                            "target_audience": target_audience,
                            "useful_context": res.get("useful_context", []),
                            "content": content,
                            "tags": res.get("tags", []),
                            "estimatedTime": res.get("estimatedTime", ""),
                            "platform_name": res.get("platform_name", ""),
                            "platform_logo_url": res.get("platform_logo_url", ""),
                            "associated_tool": res.get("associated_tool", ""),
                            "taxonomy": taxonomy,
                            "kpi_benefits": kpi_benefits,
                            "is_paid": res.get("is_paid", False),
                            "subscriptions": subscriptions,
                            "tenant_id": res.get("tenant_id", "default"),
                            "relevance_score": res["_additional"]["certainty"]
                        })
                    else:
                        # Parse metadata if it's a JSON string
                        metadata = res.get("metadata", {})
                        if isinstance(metadata, str):
                            try:
                                import json
                                metadata = json.loads(metadata)
                            except:
                                metadata = {"raw": metadata}
                                
                        documents.append({
                            "id": res["_additional"]["id"],
                            "content": res.get("content", ""),
                            "metadata": metadata,
                            "tenant_id": res.get("tenant_id", "default"),
                            "relevance_score": res["_additional"]["certainty"]
                        })
                
                return documents
            except Exception as e:
                logging.error(f"Error querying documents from Weaviate: {str(e)}")
                return []
                
    def search_ai_tools(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
            """
            Specialized function to search for AI tools using natural language queries.
            
            Args:
                query: Natural language query (e.g., "find a tool to make videos from text")
                filters: Optional filters to apply (e.g., {"category": "video"})
                limit: Maximum number of results to return
                
            Returns:
                List of AI tools matching the query
            """
            logging.info(f"Searching for AI tools with query: {query}")
            
            # Create a more comprehensive search by combining the original query with expanded context
            expanded_query = f"AI tool for {query}"
            
            # Execute the search against the Global_Tools class
            results = self.query_documents(
                query=expanded_query,
                filters=filters,
                limit=limit,
                class_name="Global_Tools"
            )
            
            # Format the results for the RAG agent
            formatted_results = []
            for i, tool in enumerate(results):
                formatted_results.append({
                    "id": tool.get("id", f"tool-{i+1}"),
                    "name": tool.get("name", "Unknown Tool"),
                    "homepage_url": tool.get("homepage_url", ""),
                    "last_scraped_at": tool.get("last_scraped_at", ""),
                    "source_urls": tool.get("source_urls", []),
                    "categories": tool.get("categories", {}),
                    "short_description": tool.get("short_description", ""),
                    "detailed_description": tool.get("detailed_description", ""),
                    "features": tool.get("features", []),
                    "differentiators": tool.get("differentiators", []),
                    "subscriptions": tool.get("subscriptions", []),
                    "compliance": tool.get("compliance", {}),
                    "documentation_links": tool.get("documentation_links", []),
                    "rating": tool.get("rating", 0.0),
                    "logo_url": tool.get("logo_url", ""),
                    "tags": tool.get("tags", []),
                    "relevance_score": tool.get("relevance_score", 0.0),
                    "citation_id": f"tool-{i+1}"
                })
            
            logging.info(f"Found {len(formatted_results)} AI tools matching the query")
            return formatted_results
            
    def search_learning_resources(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
            """
            Specialized function to search for learning resources using natural language queries.
            
            Args:
                query: Natural language query (e.g., "how to fine-tune LLMs")
                filters: Optional filters to apply (e.g., {"resource_type": "tutorial"})
                limit: Maximum number of results to return
                
            Returns:
                List of learning resources matching the query
            """
            logging.info(f"Searching for learning resources with query: {query}")
            if filters:
                logging.info(f"Applying filters: {filters}")
            
            # Create a more comprehensive search by combining the original query with expanded context
            expanded_query = f"Learning resource about {query}"
            
            # Execute the search against the Global_LearningResources class
            logging.info(f"Executing search with expanded query: {expanded_query}")
            results = self.query_documents(
                query=expanded_query,
                filters=filters,
                limit=limit,
                class_name="Global_LearningResources"
            )
            logging.info(f"Found {len(results)} initial results")
            
            # Format the results for the RAG agent
            formatted_results = []
            for i, resource in enumerate(results):
                formatted_results.append({
                    "resource_id": resource.get("resource_id", f"resource-{i+1}"),
                    "title": resource.get("title", "Unknown Resource"),
                    "content": resource.get("content", ""),
                    "url": resource.get("url", ""),
                    "author": resource.get("author", ""),
                    "resource_type": resource.get("resource_type", ""),
                    "tags": resource.get("tags", []),
                    "relevance_score": resource.get("relevance_score", 0.0),
                    "citation_id": f"resource-{i+1}"
                })
            
            logging.info(f"Found {len(formatted_results)} learning resources matching the query")
            logging.info("Top results:")
            for i, result in enumerate(formatted_results[:3]):  # Log top 3 results
                logging.info(f"{i+1}. Title: {result['title']}, Type: {result['resource_type']}, Score: {result['relevance_score']:.3f}")
            return formatted_results
            
    def search_ecosystem_partners(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
           """
           Specialized function to search for ecosystem partners using natural language queries.
           
           Args:
               query: Natural language query (e.g., "supply chain experts")
               filters: Optional filters to apply (e.g., {"budget_tier": "enterprise"})
               limit: Maximum number of results to return
               
           Returns:
               List of ecosystem partners matching the query
           """
           logging.info(f"Searching for ecosystem partners with query: {query}")
           
           # Create a more comprehensive search by combining the original query with expanded context
           expanded_query = f"Expert in {query}"
           
           # Log the current schema to verify the Global_Ecosystem class exists
           try:
               schema = self.client.schema.get()
               classes = [cls.get("class") for cls in schema.get("classes", [])]
               logging.info(f"Available Weaviate classes: {classes}")
               
               # Check if Global_Ecosystem exists
               if "Global_Ecosystem" not in classes:
                   logging.error("Global_Ecosystem class not found in schema!")
                   # Try to create it if it doesn't exist
                   self._create_global_ecosystem_class()
           except Exception as schema_error:
               logging.error(f"Error checking schema: {str(schema_error)}")
           
           # Define properties to retrieve for Global_Ecosystem class
           properties = [
               "name", "bio", "expertise", "certifications", "case_studies",
               "website", "contact_info", "budget_tier", "partner_id",
               "tags", "content", "tenant_id"
           ]
           
           # Build and execute query directly
           try:
               near_text = {"concepts": [expanded_query]}
               query_builder = (
                   self.client.query
                   .get("Global_Ecosystem", properties)
                   .with_near_text(near_text)
                   .with_limit(limit)
                   .with_additional(["id", "certainty"])
               )
               
               # Add filters if provided
               if filters:
                   where_filter = self._build_where_filter(filters)
                   if where_filter:
                       query_builder = query_builder.with_where(where_filter)
               
               result = query_builder.do()
               
               # Process results
               results = []
               for res in result.get("data", {}).get("Get", {}).get("Global_Ecosystem", []):
                   results.append({
                       "id": res["_additional"]["id"],
                       "partner_id": res.get("partner_id", ""),
                       "name": res.get("name", "Unknown Partner"),
                       "bio": res.get("bio", ""),
                       "expertise": res.get("expertise", []),
                       "certifications": res.get("certifications", []),
                       "case_studies": res.get("case_studies", ""),
                       "website": res.get("website", ""),
                       "contact_info": res.get("contact_info", ""),
                       "budget_tier": res.get("budget_tier", ""),
                       "tags": res.get("tags", []),
                       "content": res.get("content", ""),
                       "tenant_id": res.get("tenant_id", "default"),
                       "relevance_score": res["_additional"]["certainty"]
                   })
           except Exception as e:
               logging.error(f"Error querying Global_Ecosystem from Weaviate: {str(e)}")
               results = []
           
           # Log the search results for debugging
           logging.info(f"Search results count: {len(results)}")
           
           # Format the results for the RAG agent
           formatted_results = []
           for i, partner in enumerate(results):
               formatted_results.append({
                   "partner_id": partner.get("partner_id", f"partner-{i+1}"),
                   "name": partner.get("name", "Unknown Partner"),
                   "bio": partner.get("bio", ""),
                   "expertise": partner.get("expertise", []),
                   "certifications": partner.get("certifications", []),
                   "case_studies": partner.get("case_studies", ""),
                   "website": partner.get("website", ""),
                   "contact_info": partner.get("contact_info", ""),
                   "budget_tier": partner.get("budget_tier", ""),
                   "tags": partner.get("tags", []),
                   "relevance_score": partner.get("relevance_score", 0.0),
                   "citation_id": f"partner-{i+1}"
               })
           
           logging.info(f"Found {len(formatted_results)} ecosystem partners matching the query")
           return formatted_results
            
    def add_global_tool(self, tool_data: Dict[str, Any], tenant_id: str = "global") -> str:
            """
            Add an AI tool to the Global_Tools class.
            
            Args:
                tool_data: Dictionary containing tool data
                tenant_id: Tenant ID (default: "global")
                
            Returns:
                ID of the created tool
            """
            import time
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            try:
                import json
                from datetime import datetime, timezone
                
                # Generate a tool ID if not provided
                tool_id = tool_data.get("tool_id", str(uuid.uuid4()))
                
                # Store categories as JSON to maintain nested structure
                categories = tool_data.get('categories', {})
                categories_json = json.dumps(categories)
                primary_category = categories.get('primary', '')
                secondary_categories = categories.get('secondary', [])
                
                # Transform features from array of objects to JSON string
                features = tool_data.get('features', [])
                features_json = json.dumps(features) if features else "[]"
                
                # Transform subscriptions from array of objects to JSON string
                subscriptions = tool_data.get('subscriptions', [])
                subscriptions_json = json.dumps(subscriptions) if subscriptions else "[]"
                
                # Transform compliance from object to JSON string
                compliance = tool_data.get('compliance', {})
                compliance_json = json.dumps(compliance) if compliance else "{}"
                
                # Format last_scraped_at to RFC3339
                last_scraped_at = tool_data.get('last_scraped_at')
                if not last_scraped_at:
                    last_scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(last_scraped_at, str):
                    try:
                        if isinstance(last_scraped_at, datetime):
                            last_scraped_at = last_scraped_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                        else:
                            dt = datetime.fromisoformat(last_scraped_at.replace('Z', '+00:00'))
                            last_scraped_at = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        last_scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(last_scraped_at, datetime):
                    last_scraped_at = last_scraped_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Create combined content for better embedding
                content = f"Tool name: {tool_data.get('name', '')}\n"
                content += f"Short description: {tool_data.get('short_description', '')}\n"
                content += f"Detailed description: {tool_data.get('detailed_description', '')}\n"
                content += f"Primary category: {primary_category}\n"
                content += f"Secondary categories: {', '.join(secondary_categories)}\n"
                content += f"Features:\n"
                for feature in features:
                    content += f"- {feature.get('name')}: {feature.get('description')}\n"
                    content += f"  Use case: {feature.get('use_case')}\n"
                content += f"Differentiators:\n"
                for diff in tool_data.get('differentiators', []):
                    content += f"- {diff}\n"
                
                # Prepare data object for Weaviate
                data_object = {
                    "name": tool_data.get('name', ''),
                    "homepage_url": tool_data.get('homepage_url', ''),
                    "last_scraped_at": last_scraped_at,
                    "source_urls": tool_data.get('source_urls', []),
                    "categories_json": categories_json,
                    "short_description": tool_data.get('short_description', ''),
                    "detailed_description": tool_data.get('detailed_description', ''),
                    "features_json": features_json,
                    "differentiators": tool_data.get('differentiators', []),
                    "subscriptions_json": subscriptions_json,
                    "compliance_json": compliance_json,
                    "documentation_links": tool_data.get('documentation_links', []),
                    "rating": tool_data.get('rating', 0.0),
                    "logo_url": tool_data.get('logo_url', ''),
                    "tags": tool_data.get('tags', []),
                    "tenant_id": tenant_id,
                    "content": content
                }
                
                # Create embedding for the content
                logging.info("Creating embedding for global tool content...")
                embedding = self.create_embedding(content)
                logging.info(f"Embedding created with {len(embedding)} dimensions")
                
                # Create a custom session with longer timeout and retry logic
                session = requests.Session()
                retry_strategy = Retry(
                    total=5,
                    backoff_factor=2,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST", "GET", "PUT"]
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # Store the original session
                original_session = self.client._connection._session
                
                # Implement manual retry logic for timeout errors
                max_attempts = 3
                last_error = None
                
                for attempt in range(max_attempts):
                    try:
                        logging.info(f"Attempting to add tool to Weaviate (attempt {attempt + 1}/{max_attempts})...")
                        
                        # Replace with our custom session temporarily
                        self.client._connection._session = session
                        
                        # Add to Weaviate with extended timeout
                        obj_id = self.client.data_object.create(
                            class_name="Global_Tools",
                            data_object=data_object,
                            vector=embedding
                        )
                        
                        logging.info(f"Added tool to Global_Tools with ID: {obj_id}")
                        logging.info(f"Tool details - Name: {tool_data.get('name')}, Primary Category: {primary_category}")
                        logging.info(f"Last scraped at: {last_scraped_at}")
                        logging.info(f"Features count: {len(features)}, Subscriptions count: {len(subscriptions)}")
                        
                        # Restore the original session
                        self.client._connection._session = original_session
                        
                        return tool_id
                        
                    except (requests.exceptions.ReadTimeout, requests.exceptions.Timeout) as timeout_error:
                        last_error = timeout_error
                        logging.warning(f"Timeout on attempt {attempt + 1}/{max_attempts}: {str(timeout_error)}")
                        
                        if attempt < max_attempts - 1:
                            wait_time = (attempt + 1) * 5  # Progressive backoff: 5s, 10s, 15s
                            logging.info(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            logging.error(f"Failed to add tool after {max_attempts} attempts due to timeout")
                            raise
                    except Exception as e:
                        # Restore original session on any error
                        self.client._connection._session = original_session
                        raise
                    finally:
                        # Always restore the original session
                        self.client._connection._session = original_session
                
                # If we get here, all attempts failed
                if last_error:
                    raise last_error
                    
            except Exception as e:
                logging.error(f"Error adding global tool: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
                raise
                
    def add_learning_resource(self, resource_data: Dict[str, Any], tenant_id: str = "global") -> str:
            """
            Add a learning resource to the Global_LearningResources class.
            Stores data in JSON format to maintain the exact payload structure.
            
            Args:
                resource_data: Dictionary containing resource data
                tenant_id: Tenant ID (default: "global")
                
            Returns:
                ID of the created resource
            """
            import json
            from datetime import datetime, timezone
            
            logging.info("=" * 80)
            logging.info(f"=== ADDING LEARNING RESOURCE TO WEAVIATE ===")
            logging.info(f"Adding learning resource to Global_LearningResources for tenant {tenant_id}")
            logging.info(f"Resource data: title='{resource_data.get('title')}', type='{resource_data.get('resource_type')}'")
            logging.info(f"Full resource data received: {resource_data}")
            try:
                # Generate a resource ID if not provided
                resource_id = resource_data.get("resource_id", str(uuid.uuid4()))
                logging.info(f"Resource ID: {resource_id}")
                
                # Store categories as JSON to maintain nested structure
                categories = resource_data.get("categories", {})
                categories_json = json.dumps(categories)
                logging.info(f"Categories JSON: {categories_json}")
                
                # Store target_audience as JSON to maintain nested structure
                target_audience = resource_data.get("target_audience", {})
                target_audience_json = json.dumps(target_audience)
                logging.info(f"Target Audience JSON: {target_audience_json}")
                
                # Store content as JSON to maintain nested structure including null values
                content_data = resource_data.get("content", {})
                content_json = json.dumps(content_data)
                logging.info(f"Content JSON: {content_json}")
                
                # Store taxonomy as JSON if present
                taxonomy = resource_data.get("taxonomy", None)
                taxonomy_json = json.dumps(taxonomy) if taxonomy else None
                
                # Store kpi_benefits as JSON if present
                kpi_benefits = resource_data.get("kpi_benefits", None)
                kpi_benefits_json = json.dumps(kpi_benefits) if kpi_benefits else None
                
                # Store subscriptions as JSON if present
                subscriptions = resource_data.get("subscriptions", None)
                subscriptions_json = json.dumps(subscriptions) if subscriptions else None
                
                # Create combined content for embedding (only for searchability)
                combined_content = f"Title: {resource_data.get('title', '')}\n"
                combined_content += f"Description: {resource_data.get('description', '')}\n"
                combined_content += f"Summary: {content_data.get('summary', '')}\n"
                combined_content += f"Full Text Markdown: {content_data.get('full_text_markdown', '')}\n"
                learning_objectives = content_data.get('learning_objectives', [])
                if learning_objectives:
                    combined_content += f"Learning Objectives:\n"
                    for obj in learning_objectives:
                        combined_content += f"- {obj}\n"
                if content_data.get('video_transcript'):
                    combined_content += f"Video Transcript: {content_data['video_transcript']}\n"
                combined_content += f"Topics: {', '.join(resource_data.get('topics_discussed', []))}\n"
                if resource_data.get('platform_name'):
                    combined_content += f"Platform: {resource_data.get('platform_name', '')}\n"
                if resource_data.get('associated_tool'):
                    combined_content += f"Associated Tool: {resource_data.get('associated_tool', '')}\n"
                
                # Create embedding for the combined content
                logging.info("Generating embedding for learning resource content")
                embedding = self.create_embedding(combined_content)
                logging.info(f"Generated embedding with {len(embedding)} dimensions")
                
                # Build the clean data object for Weaviate using JSON strings for nested structures
                weaviate_data = {
                    "title": resource_data.get("title", ""),
                    "description": resource_data.get("description", ""),
                    "source_url": resource_data.get("source_url", ""),
                    "resource_type": resource_data.get("resource_type", ""),
                    "categories_json": categories_json,
                    "topics_discussed": resource_data.get("topics_discussed", []),
                    "target_audience_json": target_audience_json,
                    "useful_context": resource_data.get("useful_context", []),
                    "content_json": content_json,
                    "tags": resource_data.get("tags", []),
                    "estimatedTime": resource_data.get("estimatedTime", ""),
                    "platform_name": resource_data.get("platform_name", ""),
                    "platform_logo_url": resource_data.get("platform_logo_url", ""),
                    "associated_tool": resource_data.get("associated_tool", ""),
                    "taxonomy_json": taxonomy_json,
                    "kpi_benefits_json": kpi_benefits_json,
                    "is_paid": resource_data.get("is_paid", False),
                    "subscriptions_json": subscriptions_json,
                    "resource_id": resource_id,
                    "tenant_id": tenant_id
                }
                
                # Add to Weaviate
                logging.info("Adding learning resource to Weaviate with comprehensive JSON structure:")
                logging.info(f"  - Title: {weaviate_data.get('title')}")
                logging.info(f"  - Description: {weaviate_data.get('description')[:100]}..." if len(weaviate_data.get('description', '')) > 100 else f"  - Description: {weaviate_data.get('description')}")
                logging.info(f"  - Source URL: {weaviate_data.get('source_url')}")
                logging.info(f"  - Resource Type: {weaviate_data.get('resource_type')}")
                logging.info(f"  - Platform: {weaviate_data.get('platform_name')}")
                logging.info(f"  - Associated Tool: {weaviate_data.get('associated_tool')}")
                logging.info(f"  - Categories (JSON): {categories_json}")
                logging.info(f"  - Topics Discussed: {weaviate_data.get('topics_discussed')}")
                logging.info(f"  - Target Audience (JSON): {target_audience_json}")
                logging.info(f"  - Useful Context: {weaviate_data.get('useful_context')}")
                logging.info(f"  - Content (JSON): {content_json[:200]}..." if len(content_json) > 200 else f"  - Content (JSON): {content_json}")
                logging.info(f"  - Taxonomy (JSON): {taxonomy_json}")
                logging.info(f"  - KPI Benefits (JSON): {kpi_benefits_json}")
                logging.info(f"  - Is Paid: {weaviate_data.get('is_paid')}")
                logging.info(f"  - Subscriptions (JSON): {subscriptions_json}")
                logging.info(f"  - Tags: {weaviate_data.get('tags')}")
                logging.info(f"  - Estimated Time: {weaviate_data.get('estimatedTime')}")
                
                obj_id = self.client.data_object.create(
                    class_name="Global_LearningResources",
                    data_object=weaviate_data,
                    vector=embedding
                )
                logging.info("=" * 80)
                logging.info(f"✓ Successfully added resource to Global_LearningResources with ID: {obj_id}")
                logging.info(f"✓ Resource stored with comprehensive JSON structure matching new payload")
                logging.info(f"✓ All nested structures stored as JSON (preserves null values)")
                logging.info("=" * 80)
                logging.info(f"=== LEARNING RESOURCE ADDED TO WEAVIATE ===")
                logging.info("=" * 80)
                
                return resource_id
            except Exception as e:
                logging.error(f"Error adding learning resource: {str(e)}")
                raise
                
    def add_ecosystem_partner(self, partner_data: Dict[str, Any], tenant_id: str = "global") -> str:
           """
           Add an ecosystem partner to the Global_Ecosystem class.
           
           Args:
               partner_data: Dictionary containing partner data
               tenant_id: Tenant ID (default: "global")
               
           Returns:
               ID of the created partner
           """
           try:
               # Generate a partner ID if not provided
               partner_id = partner_data.get("partner_id", str(uuid.uuid4()))
               partner_data["partner_id"] = partner_id
               
               # Ensure tenant_id is set
               partner_data["tenant_id"] = tenant_id
               
               # Create combined content for better embedding
               content = f"Partner name: {partner_data.get('name', '')}\n"
               content += f"Bio: {partner_data.get('bio', '')}\n"
               content += f"Expertise: {', '.join(partner_data.get('expertise', []))}\n"
               content += f"Case studies: {partner_data.get('case_studies', '')}\n"
               
               # Add content to partner_data
               partner_data["content"] = content
               
               # Create embedding for the content
               embedding = self.create_embedding(content)
               
               # Add to Weaviate directly using data_object.create instead of add_document
               try:
                   # Create data object directly
                   data_object = {
                       "name": partner_data.get("name", ""),
                       "bio": partner_data.get("bio", ""),
                       "expertise": partner_data.get("expertise", []),
                       "certifications": partner_data.get("certifications", []),
                       "case_studies": partner_data.get("case_studies", ""),
                       "website": partner_data.get("website", ""),
                       "contact_info": partner_data.get("contact_info", ""),
                       "budget_tier": partner_data.get("budget_tier", ""),
                       "partner_id": partner_id,
                       "tags": partner_data.get("tags", []),
                       "content": content,
                       "tenant_id": tenant_id
                   }
                   
                   obj_id = self.client.data_object.create(
                       class_name="Global_Ecosystem",
                       data_object=data_object,
                       vector=embedding
                   )
                   logging.info(f"Added partner to Global_Ecosystem with ID: {obj_id}")
                   
                   # Verify the object was created
                   try:
                       result = self.client.data_object.get(class_name="Global_Ecosystem", uuid=obj_id)
                       logging.info(f"Successfully verified object in Global_Ecosystem: {result}")
                   except Exception as verify_error:
                       logging.error(f"Error verifying object in Global_Ecosystem: {str(verify_error)}")
                   
               except Exception as e:
                   logging.error(f"Error creating Weaviate object: {str(e)}")
                   raise
               
               return partner_id
           except Exception as e:
               logging.error(f"Error adding ecosystem partner: {str(e)}")
               raise
   
    def add_object(self, collection_name: str, data_object: Dict[str, Any]) -> str:
       """
       Add an object to the specified Weaviate collection.
       
       Args:
           collection_name: Name of the Weaviate class/collection
           data_object: Dictionary containing object data
           
       Returns:
           UUID of the created object
       """
       try:
           import json
           
           # Create combined content for embedding based on the collection
           if collection_name == "NoCodeTemplates":
               content = f"Template name: {data_object.get('name', '')}\n"
               content += f"Platform: {data_object.get('platform', '')}\n"
               content += f"Description: {data_object.get('short_description', '')}\n"
               content += f"Use cases: {', '.join(data_object.get('use_cases', []))}\n"
               content += f"Concrete tasks: {', '.join(data_object.get('concrete_tasks', []))}\n"
               content += f"Required connections: {', '.join(data_object.get('required_connections', []))}\n"
               content += f"Complexity: {data_object.get('complexity', '')}\n"
               
               # Extract and store categories as JSON
               categories = data_object.get('categories', {})
               categories_json = json.dumps(categories)
               
               # Extract and store taxonomy as JSON
               taxonomy = data_object.get('taxonomy', {})
               taxonomy_json = json.dumps(taxonomy)
               
               # Extract and store target_audience as JSON
               target_audience = data_object.get('target_audience', {})
               target_audience_json = json.dumps(target_audience)
               
               # Extract and store kpi_benefits as JSON
               kpi_benefits = data_object.get('kpi_benefits', {})
               kpi_benefits_json = json.dumps(kpi_benefits) if kpi_benefits else None
               
               # Prepare the data object for Weaviate
               weaviate_data = {
                   "name": data_object.get('name', ''),
                   "source_url": data_object.get('source_url', ''),
                   "platform": data_object.get('platform', ''),
                   "platform_logo_url": data_object.get('platform_logo_url', ''),
                   "use_cases": data_object.get('use_cases', []),
                   "short_description": data_object.get('short_description', ''),
                   "complexity": data_object.get('complexity', ''),
                   "categories_json": categories_json,
                   "concrete_tasks": data_object.get('concrete_tasks', []),
                   "required_connections": data_object.get('required_connections', []),
                   "taxonomy_json": taxonomy_json,
                   "target_audience_json": target_audience_json,
                   "kpi_benefits_json": kpi_benefits_json,
                   "blueprint_json_url": data_object.get('blueprint_json_url', ''),
                   "uuid": data_object.get('uuid', str(uuid.uuid4())),
                   "tenant_id": data_object.get('tenant_id', 'default'),
                   "content": content
               }
           else:
               # For other collections, use generic content
               content = str(data_object)
               weaviate_data = data_object
           
           # Create embedding for the content
           embedding = self.create_embedding(content)
           
           # Add to Weaviate
           obj_id = self.client.data_object.create(
               class_name=collection_name,
               data_object=weaviate_data,
               vector=embedding
           )
           
           logging.info(f"Added object to {collection_name} with ID: {obj_id}")
           return obj_id
           
       except Exception as e:
           logging.error(f"Error adding object to {collection_name}: {str(e)}")
           raise
            
    def add_tenant_uploaded_file(self, file_data: Dict[str, Any], organization_id: str, tenant_id: str) -> str:
            """
            Add a tenant uploaded file to the Tenant_UploadedFiles class.
            
            Args:
                file_data: Dictionary containing file data
                organization_id: Organization ID that owns the file
                tenant_id: Tenant ID
                
            Returns:
                ID of the created file entry
            """
            try:
                # Generate a file ID if not provided
                file_id = file_data.get("file_id", str(uuid.uuid4()))
                file_data["file_id"] = file_id
                
                # Ensure tenant_id and organization_id are set
                file_data["tenant_id"] = tenant_id
                file_data["organization_id"] = organization_id
                
                # Set upload_date if not provided, ensuring RFC3339 format
                if "upload_date" not in file_data:
                    from datetime import datetime, timezone
                    # Format date in RFC3339 format (e.g., "2023-10-23T13:40:00Z")
                    file_data["upload_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                elif isinstance(file_data["upload_date"], str) and "." in file_data["upload_date"]:
                    # If date has microseconds, convert to RFC3339 format
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(file_data["upload_date"].replace('Z', '+00:00'))
                        file_data["upload_date"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except:
                        # If parsing fails, use current time
                        from datetime import datetime, timezone
                        file_data["upload_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Get the content chunk
                content_chunk = file_data.get("content_chunk", "")
                
                # Create embedding for the content
                embedding = self.create_embedding(content_chunk)
                
                # Create data object directly
                data_object = {
                    "file_id": file_id,
                    "file_name": file_data.get("file_name", ""),
                    "file_path": file_data.get("file_path", ""),
                    "content_chunk": content_chunk,
                    "organization_id": organization_id,
                    "upload_date": file_data.get("upload_date", ""),
                    "file_type": file_data.get("file_type", ""),
                    "tags": file_data.get("tags", []),
                    "tenant_id": tenant_id
                }
                
                # Add to Weaviate
                try:
                    obj_id = self.client.data_object.create(
                        class_name="Tenant_UploadedFiles",
                        data_object=data_object,
                        vector=embedding
                    )
                    logging.info(f"Added file to Tenant_UploadedFiles with ID: {obj_id}")
                except Exception as e:
                    logging.error(f"Error creating Weaviate object: {str(e)}")
                    raise
                
                return file_id
            except Exception as e:
                logging.error(f"Error adding tenant uploaded file: {str(e)}")
                raise
                
    def search_tenant_uploaded_files(self, query: str, organization_id: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
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
                
                # Execute the query
                result = query_builder.do()
                
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
                
            except Exception as e:
                logging.error(f"Error searching tenant uploaded files: {str(e)}")
                import traceback
                logging.error(traceback.format_exc())
                return []
            
    def _query_with_vector(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Query using vector similarity with the provided query"""
        try:
            # Create the embedding for the query
            query_embedding = self.create_embedding(query)
            
            # Build the query
            query_builder = (
                self.client.query
                .get("Document", ["content", "metadata", "tenant_id", "_additional {certainty}"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
            )
            
            # Add filters if provided
            if filters:
                where_filter = self._build_where_filter(filters)
                if where_filter:
                    query_builder = query_builder.with_where(where_filter)
            
            # Execute the query
            result = query_builder.do()
            
            # Process the results
            return self._process_query_results(result)
        except Exception as e:
            logging.error(f"Error in vector query: {str(e)}")
            return []
            
    def _query_with_text(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Query using text similarity with the provided query string"""
        try:
            # Build the query
            query_builder = (
                self.client.query
                .get("Document", ["content", "metadata", "tenant_id", "_additional {certainty}"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
            )
            
            # Add filters if provided
            if filters:
                where_filter = self._build_where_filter(filters)
                if where_filter:
                    query_builder = query_builder.with_where(where_filter)
            
            # Execute the query
            result = query_builder.do()
            
            # Process the results
            return self._process_query_results(result)
        except Exception as e:
            logging.error(f"Error in text query: {str(e)}")
            return []
            
    def _query_without_filters(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query without any filters to find any potentially relevant documents"""
        try:
            # Create the embedding for the query
            query_embedding = self.create_embedding(query)
            
            # Build the query without filters
            query_builder = (
                self.client.query
                .get("Document", ["content", "metadata", "tenant_id", "_additional {certainty}"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
            )
            
            # Execute the query
            result = query_builder.do()
            
            # Process the results
            return self._process_query_results(result)
        except Exception as e:
            logging.error(f"Error in relaxed query: {str(e)}")
            return []
            
    def _process_query_results(self, result) -> List[Dict[str, Any]]:
        """Process query results into a standard format"""
        documents = []
        if result and "data" in result and "Get" in result["data"] and "Document" in result["data"]["Get"]:
            for doc in result["data"]["Get"]["Document"]:
                try:
                    # Calculate relevance score from certainty
                    certainty = doc["_additional"]["certainty"] if "_additional" in doc and "certainty" in doc["_additional"] else 0
                    
                    # Parse metadata if it's a JSON string
                    metadata = doc.get("metadata", {})
                    if isinstance(metadata, str):
                        try:
                            import json
                            metadata = json.loads(metadata)
                        except:
                            metadata = {"raw": metadata}
                    
                    documents.append({
                        "content": doc["content"],
                        "metadata": metadata,
                        "tenant_id": doc.get("tenant_id", "default"),
                        "relevance_score": certainty
                    })
                except Exception as e:
                    logging.error(f"Error processing document result: {str(e)}")
                    continue
        
        return documents

    def _build_where_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a where filter for Weaviate queries.
        
        Args:
            filters: The filters to apply
            
        Returns:
            A Weaviate where filter
        """
        # Handle multiple filters with AND operator
        if len(filters) > 1:
            operands = []
            for key, value in filters.items():
                if key == "tenant_id":
                    operands.append({
                        "path": ["tenant_id"],
                        "operator": "Equal",
                        "valueString": value
                    })
                # Note: source is now inside metadata JSON, cannot filter directly
                # To filter by source, you would need to parse metadata in post-processing
            
            if operands:
                return {
                    "operator": "And",
                    "operands": operands
                }
            return {}
        
        # Handle single filter
        where_filter = {}
        
        if "tenant_id" in filters:
            where_filter["path"] = ["tenant_id"]
            where_filter["operator"] = "Equal"
            where_filter["valueString"] = filters["tenant_id"]
        # Note: source is now inside metadata JSON, cannot filter directly
        # To filter by source, you would need to parse metadata in post-processing
        
        return where_filter

    def langchain_similarity_search(self, query: str, tenant_id: str, k: int = 5) -> List[Any]:
        """
        Perform similarity search using LangChain's Weaviate integration.
        
        Args:
            query: The query string
            tenant_id: The tenant ID to filter results by
            k: Number of results to return
            
        Returns:
            List of documents matching the query
        """
        if not LANGCHAIN_AVAILABLE:
            logging.warning("LangChain is not available. Falling back to standard semantic search.")
            # Create embedding and use standard semantic search as fallback
            query_embedding = self.create_embedding(query)
            results = self.semantic_search(query_embedding, tenant_id, limit=k)
            
            # Convert to a format similar to LangChain's Document objects
            return [{"page_content": doc["content"], "metadata": doc["metadata"]} for doc in results]
        
        # Create filter for tenant_id
        filter_dict = {
            "path": ["tenant_id"],
            "operator": "Equal",
            "valueString": tenant_id
        }
        
        # Use LangChain's similarity search
        docs = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        return docs

    def close(self):
        """
        Close the Weaviate client.
        """
        # Weaviate client doesn't have a close method
        # This is here for consistency with other clients
        pass
