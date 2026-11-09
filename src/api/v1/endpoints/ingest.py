
from typing import Annotated, Dict, Any
from uuid import uuid4
import logging
import os
import requests
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status, UploadFile, File
from fastapi.routing import APIRouter

from src.api.v1.schemas import (
    IngestDocumentRequest,
    IngestUrlRequest,
    IngestFileRequest,
    IngestResponse,
    GlobalToolIngestionRequest,
    GlobalLearningResourceIngestionRequest,
    GlobalEcosystemPartnerIngestionRequest,
    NoCodeTemplateIngestionRequest,
    PreMadePromptIngestionRequest,
    TenantUploadedFile,
    GCSFileIngestionRequest,
    GCSFileIngestionState,
    ChunkTextRequest,
    ChunkTextResponse,
    GenerateEmbeddingsRequest,
    GenerateEmbeddingsResponse,
    PersistToWeaviateRequest,
    PersistToWeaviateResponse,
    PersistToNeo4jRequest,
    PersistToNeo4jResponse
)
from src.api.dependencies import get_ingestion_graph, get_current_user
from src.ingestion.graph import IngestionGraph
from src.data_stores.global_tools_client import NoCodeTemplatesClient, NoCodeTemplate, GlobalLearningResourcesClient, GlobalLearningResource, GlobalToolsClient, GlobalTool, PreMadePromptsClient, PreMadePrompt
import httpx

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest/document", response_model=IngestResponse, tags=["ingestion"])
async def ingest_document(
    request: IngestDocumentRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Ingest Document: Process and store document content directly provided in the request.
    """
    logger.info(f"Starting document content ingestion for tenant {request.tenant_id}")

    # Handle the created_at field: if empty string or None, set current time
    if request.metadata and request.metadata.created_at in [None, ""]:
        # Set current datetime if not provided or empty
        request.metadata.created_at = datetime.utcnow().isoformat() + "Z"
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    
    # Prepare input data
    input_data = {
        "content": request.content,
        "metadata": request.metadata.model_dump() if request.metadata else {},
        "job_id": job_id,
        "source_type": "document"
    }
    
    try:
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id=request.tenant_id
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting document: {str(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest document: {str(result)}",
            )
            
        logger.info(f"Document ingestion started with job ID: {job_id}")
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="Document ingestion started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        ) from e


@router.post("/ingest/url", response_model=IngestResponse, tags=["ingestion"])
async def ingest_url(
    request: IngestUrlRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Ingest URL: Fetch content from the provided URL and process it.
    """
    logger.info(f"Starting URL content ingestion for tenant {request.tenant_id}: {request.url}")
    
    # Handle the created_at field: if empty string or None, set current time
    if request.metadata and request.metadata.created_at in [None, ""]:
        # Set current datetime if not provided or empty
        request.metadata.created_at = datetime.utcnow().isoformat() + "Z"
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    
    try:
        # Fetch content from URL
        response = requests.get(request.url, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        content = response.text
        
        # Prepare metadata with URL as source
        metadata = request.metadata.model_dump() if request.metadata else {}
        if "source" not in metadata or not metadata["source"]:
            metadata["source"] = request.url
            
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": metadata,
            "job_id": job_id,
            "source_type": "url",
            "url": request.url
        }
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id=request.tenant_id
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting URL content: {str(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest URL content: {str(result)}",
            )
            
        logger.info(f"URL ingestion started with job ID: {job_id}")
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="URL ingestion started successfully"
        )
        
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {request.url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch content from URL: {str(e)}",
        ) from e
        
    except Exception as e:
        logger.error(f"Error ingesting URL content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest URL content: {str(e)}",
        ) from e


@router.post("/ingest/file", response_model=IngestResponse, tags=["ingestion"])
async def ingest_file(
    file: UploadFile = File(...),
    tenant_id: str = "default",
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)] = None,
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))] = None,
):
    """
    Ingest File: Process and store content from an uploaded file.
    """
    logger.info(f"Starting file content ingestion for tenant {tenant_id}: {file.filename}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    
    try:
        # Create a temporary file to store the uploaded content
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_path = temp_file.name
            
            # Write uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        try:
            # Prepare metadata with filename as source
            metadata = {
                "source": file.filename,
                "content_type": file.content_type,
                "file_size": len(content)
            }
                
            # Prepare input data
            input_data = {
                "file_path": temp_path,
                "metadata": metadata,
                "job_id": job_id,
                "source_type": "file",
                "filename": file.filename
            }
            
            # Start async ingestion
            result = await ingestion_graph.ingest_document_async(
                input_data=input_data,
                tenant_id=tenant_id
            )
            
            if isinstance(result, Exception):
                logger.error(f"Error ingesting file content: {str(result)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to ingest file content: {str(result)}",
                )
                
            logger.info(f"File ingestion started with job ID: {job_id}")
            
            # Return job ID with status information
            return IngestResponse(
                job_id=job_id,
                status_code=200,
                status_message="File ingestion started successfully"
            )
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error ingesting file content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest file content: {str(e)}",
        ) from e


# Keep the original endpoint for backward compatibility
@router.post("/ingest", response_model=IngestResponse, tags=["ingestion"], deprecated=True)
async def ingest_content(
    request: IngestDocumentRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    [DEPRECATED] Use /rag/ingest/document instead.
    Trigger LangGraph ingestion graph async and return job_id.
    """
    logger.warning("Using deprecated /ingest endpoint. Please migrate to /rag/ingest/document")
    return await ingest_document(request, current_user, ingestion_graph)


# Global Knowledge Domain Endpoints

@router.post("/ingest/global/tool", response_model=IngestResponse, tags=["ingestion"])
async def ingest_global_tool(
    request: GlobalToolIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("global_tool_ingestion_graph"))],
):
    """
    Ingest AI Tool: Process and store AI tool data in the global knowledge domain.
    Also sends the tool data to the global tools service via connector.
    """
    logger.info(f"Starting AI tool ingestion for global knowledge domain - Tool: {request.name}")
    logger.debug(f"Tool data received: {request.model_dump_json(indent=2)}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    try:
        # ------------------------------------------------------------------
        # Normalize & validate last_scraped_at (INLINE FIX)
        # ------------------------------------------------------------------
        if not request.last_scraped_at:
            last_scraped_dt = datetime.now(timezone.utc)
        else:
            try:
                last_scraped_dt = datetime.fromisoformat(
                    request.last_scraped_at.replace("Z", "+00:00")
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid last_scraped_at format. Expected RFC3339 / ISO-8601."
                )
            
        # Prepare tool data
        tool_data = request.model_dump(exclude={"tenant_id"})
        logger.debug(f"Prepared tool data for processing: {tool_data}")
        tool_data["last_scraped_at"] = last_scraped_dt
        
        # Initialize global tools client and create GlobalTool instance

        # from src.data_stores.global_tools_client import GlobalToolsClient, GlobalTool
        # import httpx   
        
        try:
            logger.info("Initializing GlobalToolsClient for connector operation")
            client = GlobalToolsClient()
            global_tool = GlobalTool(**tool_data)
            logger.info(f"Created GlobalTool instance for '{request.name}'")
            
            # Send to global tools service (optional - continue on failure)
            global_service_success = False
            try:
                logger.info(f"Sending tool '{request.name}' to global tools service via connector...")
                global_response = await client.add_global_tool(global_tool)

                # Check if this was a duplicate tool response
                if global_response.get("duplicate"):
                    logger.info(f"Tool '{request.name}' already exists in global service - proceeding with local ingestion")
                else:
                    logger.info(f"Successfully sent tool '{request.name}' to global tools service")
                    global_service_success = True
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error from global tools service: {e.response.status_code} - {e.response.text}. Continuing with local ingestion only.")
            except httpx.RequestError as e:
                logger.warning(f"Network error connecting to global tools service: {str(e)}. Continuing with local ingestion only.")
            except ValueError as e:
                logger.warning(f"Validation error for global tool: {str(e)}. Continuing with local ingestion only.")
            except Exception as e:
                logger.warning(f"Unexpected error with global tools service: {str(e)}. Continuing with local ingestion only.")
        except Exception as e:
            logger.error(f"Error initializing global tools client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize global tools client: {str(e)}"
            )
        
        # Create content for embedding after successful global service update
        content = f"Tool name: {tool_data.get('name', '')}\n"
        content += f"Short description: {tool_data.get('short_description', '')}\n"
        content += f"Detailed description: {tool_data.get('detailed_description', '')}\n"
        content += f"Primary category: {tool_data.get('categories', {}).get('primary', '')}\n"
        content += f"Secondary categories: {', '.join(tool_data.get('categories', {}).get('secondary', []))}\n"
        content += f"Features:\n"
        for feature in tool_data.get('features', []):
            content += f"- {feature.get('name')}: {feature.get('description')}\n"
            content += f"  Use case: {feature.get('use_case')}\n"
        content += f"Differentiators:\n"
        for diff in tool_data.get('differentiators', []):
            content += f"- {diff}\n"
        
        logger.info("Tool data successfully processed by global service, proceeding with local ingestion")
        
        # Validate required fields
        if not tool_data.get('name'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool name is required"
            )
            
        if not tool_data.get('short_description'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short description is required"
            )
            
        if not tool_data.get('categories') or not tool_data['categories'].get('primary'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primary category is required"
            )
            
        # Validate URLs
        try:
            str(request.homepage_url)
            [str(url) for url in request.source_urls]
            [str(url) for url in request.documentation_links]
            if request.logo_url:
                str(request.logo_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid URL format: {str(e)}"
            )
            
        # Validate date format
        # try:
        #     from datetime import datetime
        #     datetime.fromisoformat(request.last_scraped_at.replace('Z', '+00:00'))
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Invalid date format for last_scraped_at. Expected ISO format: {str(e)}"
        #     )
            
        # Validate rating range
        if request.rating < 0 or request.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 0 and 5"
            )
            
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": {
                "name": request.name,
                "homepage_url": str(request.homepage_url),
                "last_scraped_at": last_scraped_dt.replace(tzinfo=None).isoformat(timespec="seconds") + "Z",
                "source_urls": [str(url) for url in request.source_urls],
                "categories": request.categories,
                "short_description": request.short_description,
                "detailed_description": request.detailed_description,
                "features": request.features,
                "differentiators": request.differentiators,
                "subscriptions": request.subscriptions,
                "compliance": request.compliance,
                "documentation_links": [str(url) for url in request.documentation_links],
                "rating": request.rating,
                "logo_url": str(request.logo_url) if request.logo_url else None,
                "tags": request.tags,
                "document_type": "global_tool"
            },
            "job_id": job_id,
            "source_type": "global_tool"
        }
        # Prepare tool data
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="global tool"  # Use global tenant for global knowledge
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting AI tool: {str(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest AI tool: {str(result)}",
            )
            
        logger.info(f"AI tool ingestion started with job ID: {job_id}")
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="AI tool ingestion started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting AI tool: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest AI tool: {str(e)}",
        ) from e


@router.post("/ingest/global/learning-resource", response_model=IngestResponse, tags=["ingestion"])
async def ingest_global_learning_resource(
    request: GlobalLearningResourceIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("global_learning_resource_ingestion_graph"))],
):
    """
    Ingest Learning Resource: Process and store learning resource data in the global knowledge domain.
    Also creates knowledge graph in Neo4j.
    """
    logger.info("=" * 80)
    logger.info(f"=== GLOBAL LEARNING RESOURCE INGESTION STARTED ===")
    logger.info("=" * 80)
    logger.info(f"Starting learning resource ingestion for global knowledge domain - Resource: {request.title}")
    logger.info(f"Resource Type: {request.resource_type}")
    
    # Handle categories safely - check if it's a Pydantic model or dict
    categories = request.categories if hasattr(request.categories, 'primary') else request.categories
    if hasattr(categories, 'primary'):
        logger.info(f"Categories: Primary='{categories.primary}', Secondary={categories.secondary}")
    else:
        logger.info(f"Categories: {categories}")
    
    logger.info(f"Topics Discussed: {request.topics_discussed}")
    
    # Handle target_audience safely
    target_audience = request.target_audience if hasattr(request.target_audience, 'expertise_level') else request.target_audience
    if hasattr(target_audience, 'expertise_level'):
        logger.info(f"Target Audience: Level={target_audience.expertise_level}, Roles={target_audience.job_roles}")
    else:
        logger.info(f"Target Audience: {target_audience}")
    
    logger.info(f"Useful Context: {request.useful_context}")
    logger.info(f"Tags: {request.tags}")
    logger.info(f"Platform Name: {request.platform_name}")
    logger.info(f"Associated Tool: {request.associated_tool}")
    logger.info(f"Taxonomy: {request.taxonomy}")
    logger.info(f"KPI Benefits: {request.kpi_benefits}")
    logger.info(f"Subscriptions: {request.subscriptions}")
    logger.debug(f"Full learning resource payload: {request.model_dump_json(indent=2)}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    try:
        # Prepare resource data
        resource_data = request.model_dump(exclude={"tenant_id"})
        logger.debug(f"Prepared resource data for processing: {resource_data}")
        
        # Handle last_scraped_at field - set to current time if not provided
        if not resource_data.get('last_scraped_at'):
            resource_data['last_scraped_at'] = datetime.now(timezone.utc)
        else:
            try:
                # Parse the ISO string to datetime object
                resource_data['last_scraped_at'] = datetime.fromisoformat(
                    resource_data['last_scraped_at'].replace("Z", "+00:00")
                )
            except Exception as e:
                logger.warning(f"Invalid last_scraped_at format, using current time: {str(e)}")
                resource_data['last_scraped_at'] = datetime.now(timezone.utc)
        
        # Initialize global learning resources client and create GlobalLearningResource instance
        
        # from src.data_stores.global_tools_client import GlobalLearningResourcesClient, GlobalLearningResource
        # import httpx
        
        try:
            logger.info("Initializing GlobalLearningResourcesClient for connector operation")
            client = GlobalLearningResourcesClient()
            learning_resource = GlobalLearningResource(**resource_data)
            logger.info(f"Created GlobalLearningResource instance for '{request.title}'")
            
            # Send to global learning resources service (optional - continue on failure)
            global_service_success = False
            try:
                logger.info(f"Sending learning resource '{request.title}' to global service via connector...")
                global_response = await client.post_learning_resource(learning_resource)

                # Check if this was a duplicate resource response
                if global_response.get("duplicate"):
                    logger.info(f"Resource '{request.title}' already exists in global service - proceeding with local ingestion")
                else:
                    logger.info(f"Successfully sent learning resource '{request.title}' to global service")
                    global_service_success = True
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error from global service: {e.response.status_code} - {e.response.text}. Continuing with local ingestion only.")
            except httpx.RequestError as e:
                logger.warning(f"Network error connecting to global service: {str(e)}. Continuing with local ingestion only.")
            except ValueError as e:
                logger.warning(f"Validation error for learning resource: {str(e)}. Continuing with local ingestion only.")
            except Exception as e:
                logger.warning(f"Unexpected error with global service: {str(e)}. Continuing with local ingestion only.")
        except Exception as e:
            logger.error(f"Error initializing global learning resources client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize global learning resources client: {str(e)}"
            )
        
        # Create content for embedding
        content = f"Title: {resource_data.get('title', '')}\n"
        content += f"Description: {resource_data.get('description', '')}\n"
        content += f"Summary: {resource_data.get('content', {}).get('summary', '')}\n"
        content += f"Full Text Markdown: {resource_data.get('content', {}).get('full_text_markdown', '')}\n"
        learning_objectives = resource_data.get('content', {}).get('learning_objectives', [])
        if learning_objectives:
            content += f"Learning Objectives:\n"
            for obj in learning_objectives:
                content += f"- {obj}\n"
        if resource_data.get('content', {}).get('video_transcript'):
            content += f"Video Transcript: {resource_data['content']['video_transcript']}\n"
        content += f"Topics: {', '.join(resource_data.get('topics_discussed', []))}\n"
        if resource_data.get('platform_name'):
            content += f"Platform: {resource_data.get('platform_name', '')}\n"
        if resource_data.get('associated_tool'):
            content += f"Associated Tool: {resource_data.get('associated_tool', '')}\n"
        if resource_data.get('taxonomy'):
            taxonomy = resource_data.get('taxonomy', {})
            content += f"Department: {taxonomy.get('department', '')}\n"
            content += f"Team Task Category: {taxonomy.get('team_task_category', '')}\n"
        
        # Validate required fields
        if not resource_data.get('title'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
            
        if not resource_data.get('description'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description is required"
            )
            
        if not resource_data.get('source_url'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source URL is required"
            )
            
        if not resource_data.get('resource_type'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource type is required"
            )
            
        # Validate URLs
        try:
            str(request.source_url)
            if request.content.video_url:
                str(request.content.video_url)
            if request.platform_logo_url:
                str(request.platform_logo_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid URL format: {str(e)}"
            )
            
        # # Validate date format
        # try:
        #     from datetime import datetime
        #     datetime.fromisoformat(request.last_scraped_at.replace('Z', '+00:00'))
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Invalid date format for last_scraped_at. Expected ISO format: {str(e)}"
        #     )
        
        logger.info("Learning resource data successfully processed by global service, proceeding with local ingestion")
        
        # Prepare input data
        # Note: resource_data already has model_dump() called
        input_data = {
            "content": content,
            "metadata": {
                "title": request.title,
                "description": request.description,
                "source_url": str(request.source_url),
                "resource_type": request.resource_type,
                "categories": request.categories.model_dump() if request.categories else {},
                "topics_discussed": request.topics_discussed,
                "target_audience": request.target_audience.model_dump() if request.target_audience else {},
                "useful_context": request.useful_context,
                "content": request.content.model_dump() if request.content else {},
                "tags": request.tags,
                "estimatedTime": request.estimatedTime,
                "platform_name": request.platform_name,
                "platform_logo_url": str(request.platform_logo_url) if request.platform_logo_url else None,
                "associated_tool": request.associated_tool,
                "taxonomy": request.taxonomy.model_dump() if request.taxonomy else None,
                "kpi_benefits": request.kpi_benefits.model_dump() if request.kpi_benefits else None,
                "is_paid": request.is_paid,
                "subscriptions": request.subscriptions.model_dump() if request.subscriptions else None,
                "document_type": "learning_resource"
            },
            "job_id": job_id,
            "source_type": "global_learning_resource"
        }
        
        logger.info("=" * 80)
        logger.info("Prepared input data for ingestion graph:")
        logger.info(f"Content length: {len(content)} characters")
        logger.info(f"Metadata fields: {list(input_data['metadata'].keys())}")
        logger.info(f"Categories in metadata: {input_data['metadata']['categories']}")
        logger.info(f"Topics in metadata: {input_data['metadata']['topics_discussed']}")
        logger.info(f"Target audience in metadata: {input_data['metadata']['target_audience']}")
        logger.info(f"Source type: {input_data['source_type']}")
        logger.info(f"Job ID: {input_data['job_id']}")
        logger.info("=" * 80)

        # Validate required fields
        if not input_data.get('content'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content cannot be empty"
            )
        if not input_data.get('metadata'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metadata cannot be empty"
            )
        if not input_data['metadata'].get('title'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required in metadata"
            )
        
        # Start async ingestion
        try:
            result = await ingestion_graph.ingest_document_async(
                input_data=input_data,
                tenant_id="global"  # Use global tenant for global knowledge
            )
        except Exception as e:
            logger.error(f"Exception during ingestion: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start ingestion: {str(e)}",
            )

        if isinstance(result, Exception):
            logger.error(f"Error ingesting learning resource: {str(result)}")
            logger.error("=" * 80)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest learning resource: {str(result)}",
            )
            
        logger.info("=" * 80)
        logger.info(f"✓ Learning resource ingestion completed with job ID: {job_id}")
        logger.info(f"✓ Resource Title: {request.title}")
        logger.info(f"✓ Resource Type: {request.resource_type}")
        logger.info(f"✓ Data successfully sent to:")
        logger.info(f"  - Weaviate (Global_LearningResources class)")
        logger.info(f"  - Neo4j (LearningResource node + relationships)")
        if global_service_success:
            logger.info(f"  - Global Learning Resources Service (new resource created)")
        else:
            logger.info(f"  - Global Learning Resources Service (existing resource or service unavailable)")
        logger.info("=" * 80)
        logger.info(f"=== GLOBAL LEARNING RESOURCE INGESTION COMPLETED ===")
        logger.info("=" * 80)
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="Learning resource ingestion started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting learning resource: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest learning resource: {str(e)}",
        ) from e


@router.post("/ingest/global/ecosystem-partner", response_model=IngestResponse, tags=["ingestion"])
async def ingest_global_ecosystem_partner(
    request: GlobalEcosystemPartnerIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("global_ecosystem_partner_ingestion_graph"))],
):
    """
    Ingest Ecosystem Partner: Process and store ecosystem partner data in the global knowledge domain.
    """
    logger.info("=" * 80)
    logger.info("=== GLOBAL ECOSYSTEM PARTNER INGESTION STARTED ===")
    logger.info("=" * 80)
    logger.info(f"Starting ecosystem partner ingestion for global knowledge domain - Partner: {request.name}")
    logger.info(f"Budget Tier: {request.budget_tier}")
    logger.info(f"Expertise: {request.expertise}")
    logger.info(f"Tags: {request.tags}")
    logger.debug(f"Full ecosystem partner payload: {request.model_dump_json(indent=2)}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    try:
        # Prepare partner data
        partner_data = request.model_dump(exclude={"tenant_id"})
        logger.debug(f"Prepared partner data for processing: {partner_data}")
        
        # Create content for embedding
        content = f"Partner name: {partner_data.get('name', '')}\n"
        content += f"Bio: {partner_data.get('bio', '')}\n"
        content += f"Expertise: {', '.join(partner_data.get('expertise', []))}\n"
        content += f"Certifications: {', '.join(partner_data.get('certifications', []))}\n"
        content += f"Case studies: {partner_data.get('case_studies', '')}\n"
        content += f"Budget tier: {partner_data.get('budget_tier', '')}\n"
        
        # Generate a partner ID if not provided
        partner_id = str(uuid4())
        
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": {
                "name": request.name,
                "bio": request.bio,
                "expertise": request.expertise,
                "certifications": request.certifications if request.certifications else [],
                "case_studies": request.case_studies,
                "website": request.website,
                "contact_info": request.contact_info,
                "budget_tier": request.budget_tier,
                "tags": request.tags if request.tags else [],
                "document_type": "ecosystem_partner",
                "partner_id": partner_id
            },
            "job_id": job_id,
            "source_type": "global_ecosystem_partner"
        }
        
        # Debug logging
        logger.info(f"Ecosystem partner input_data: {input_data}")
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="global ecosystem partner"  # Use global tenant for global knowledge
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting ecosystem partner: {str(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest ecosystem partner: {str(result)}",
            )
            
        logger.info("=" * 80)
        logger.info(f"✓ Ecosystem partner ingestion completed with job ID: {job_id}")
        logger.info(f"✓ Partner Name: {request.name}")
        logger.info(f"✓ Budget Tier: {request.budget_tier}")
        logger.info(f"✓ Data successfully sent to:")
        logger.info(f"  - Weaviate (Global_Ecosystem class)")
        logger.info(f"  - Neo4j (EcosystemPartner node + relationships)")
        logger.info("=" * 80)
        logger.info("=== GLOBAL ECOSYSTEM PARTNER INGESTION COMPLETED ===")
        logger.info("=" * 80)
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="Ecosystem partner ingestion started successfully"
        )
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"Error ingesting ecosystem partner: {str(e)}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest ecosystem partner: {str(e)}",
        ) from e


@router.post("/ingest/no-code-templates", response_model=IngestResponse, tags=["ingestion"])
async def ingest_no_code_template(
    request: NoCodeTemplateIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("no_code_template_ingestion_graph"))],
):
    """
    Ingest No-Code Template: Process and store no-code template data in the global knowledge domain.
    Creates template nodes in Neo4j with relationships to use cases, categories, and platforms.
    Also sends the template data to the global service via connector.
    """
    logger.info(f"Starting no-code template ingestion - Template: {request.name}")
    logger.debug(f"Template data received: {request.model_dump_json(indent=2)}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    try:
        # Prepare template data
        template_data = request.model_dump(exclude={"tenant_id"})
        logger.debug(f"Prepared template data for processing: {template_data}")
        
        # Initialize no-code templates client and create NoCodeTemplate instance

        # from src.data_stores.global_tools_client import NoCodeTemplatesClient, NoCodeTemplate
        # import httpx
        
        try:
            logger.info("Initializing NoCodeTemplatesClient for connector operation")
            client = NoCodeTemplatesClient()
            no_code_template = NoCodeTemplate(**template_data)
            logger.info(f"Created NoCodeTemplate instance for '{request.name}'")
            
            # Send to no-code templates service first
            try:
                logger.info(f"Sending template '{request.name}' to no-code templates service via connector...")
                await client.post_no_code_template(no_code_template)
                connector_success = True
                logger.info(f"Successfully sent template '{request.name}' to no-code templates service")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from no-code templates service: {e.response.status_code} - {e.response.text}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"No-code templates service error: {e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(f"Network error connecting to no-code templates service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No-code templates service is unavailable"
                )
            except ValueError as e:
                logger.error(f"Validation error for no-code template: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid template data: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Unexpected error with no-code templates service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing template in service: {str(e)}"
                )
        except Exception as e:
            # pass
            logger.error(f"Error initializing no-code templates client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize no-code templates client: {str(e)}"
            )
        
        # Create content for embedding after successful service update
        content = f"Template name: {template_data.get('name', '')}\n"
        content += f"Short description: {template_data.get('short_description', '')}\n"
        content += f"Platform: {template_data.get('platform', '')}\n"
        content += f"Complexity: {template_data.get('complexity', '')}\n"
        content += f"Use cases: {', '.join(template_data.get('use_cases', []))}\n"
        content += f"Concrete tasks: {', '.join(template_data.get('concrete_tasks', []))}\n"
        content += f"Required connections: {', '.join(template_data.get('required_connections', []))}\n"
        content += f"Primary category: {template_data.get('categories', {}).get('primary', '')}\n"
        content += f"Secondary categories: {', '.join(template_data.get('categories', {}).get('secondary', []))}\n"
        
        # Add taxonomy information
        taxonomy = template_data.get('taxonomy', {})
        content += f"Department: {taxonomy.get('department', '')}\n"
        content += f"Team task category: {taxonomy.get('team_task_category', '')}\n"
        content += f"Type category: {taxonomy.get('type_category', '')}\n"
        
        # Add target audience information
        target_audience = template_data.get('target_audience', {})
        content += f"Expertise level: {target_audience.get('expertise_level', '')}\n"
        content += f"Job roles: {', '.join(target_audience.get('job_roles', []))}\n"
        
        # Add KPI benefits if available
        if template_data.get('kpi_benefits'):
            kpi_benefits = template_data['kpi_benefits']
            content += f"\nKPI Benefits:\n"
            if kpi_benefits.get('estimated_time_saving'):
                content += f"- Estimated time saving: {kpi_benefits['estimated_time_saving']}\n"
            if kpi_benefits.get('efficiency_gain_percentage'):
                content += f"- Efficiency gain: {kpi_benefits['efficiency_gain_percentage']}%\n"
            if kpi_benefits.get('cost_reduction'):
                content += f"- Cost reduction: {kpi_benefits['cost_reduction']}\n"
            if kpi_benefits.get('quality_improvement_metric'):
                content += f"- Quality improvement: {kpi_benefits['quality_improvement_metric']}\n"
        
        logger.info("Template data successfully processed by service, proceeding with local ingestion")
        
        # Validate required fields
        if not template_data.get('name'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template name is required"
            )
            
        if not template_data.get('short_description'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short description is required"
            )
            
        if not template_data.get('categories') or not template_data['categories'].get('primary'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primary category is required"
            )
            
        if not template_data.get('platform'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform is required"
            )
            
        if not template_data.get('complexity'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complexity is required"
            )
            
        if not template_data.get('taxonomy') or not template_data['taxonomy'].get('department'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Taxonomy with department is required"
            )
            
        if not template_data.get('target_audience') or not template_data['target_audience'].get('expertise_level'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target audience with expertise level is required"
            )
            
        # Validate URLs
        try:
            str(request.source_url)
            if request.platform_logo_url:
                str(request.platform_logo_url)
            if request.blueprint_json_url:
                str(request.blueprint_json_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid URL format: {str(e)}"
            )
        
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": {
                "name": request.name,
                "source_url": str(request.source_url),
                "platform": request.platform,
                "platform_logo_url": request.platform_logo_url,
                "use_cases": request.use_cases,
                "short_description": request.short_description,
                "complexity": request.complexity,
                "categories": request.categories.model_dump(),
                "concrete_tasks": request.concrete_tasks,
                "required_connections": request.required_connections,
                "taxonomy": request.taxonomy.model_dump(),
                "target_audience": request.target_audience.model_dump(),
                "kpi_benefits": request.kpi_benefits.model_dump() if request.kpi_benefits else None,
                "blueprint_json_url": request.blueprint_json_url,
                "document_type": "no_code_template"
            },
            "job_id": job_id,
            "source_type": "no_code_template"
        }
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="No Code Template"  # Use No Code Template tenant for global knowledge
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting no-code template: {str(result)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest no-code template: {str(result)}",
            )
            
        logger.info(f"No-code template ingestion started with job ID: {job_id}")
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="No-code template ingestion started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting no-code template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest no-code template: {str(e)}",
        ) from e


@router.post("/ingest/pre-made-prompts", response_model=IngestResponse, tags=["ingestion"])
async def ingest_pre_made_prompt(
    request: PreMadePromptIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("pre_made_prompt_ingestion_graph"))],
):
    """
    Ingest Pre-Made Prompt: Process and store pre-made prompt data in the global knowledge domain.
    Creates prompt nodes in Neo4j with relationships to tasks, tools, categories, and KPIs.
    Also sends the prompt data to the global service via connector.
    """
    logger.info("=" * 80)
    logger.info("=== PRE-MADE PROMPT INGESTION STARTED ===")
    logger.info("=" * 80)
    logger.info(f"Starting pre-made prompt ingestion - Prompt: {request.name}")
    logger.info(f"Associated Tool: {request.associated_tool}")
    logger.info(f"Prompting Technique: {request.prompting_technique}")
    logger.info(f"Tags: {request.tags}")
    logger.debug(f"Full pre-made prompt payload: {request.model_dump_json(indent=2)}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    logger.info(f"Generated job ID: {job_id}")
    
    try:
        # Prepare prompt data
        prompt_data = request.model_dump(exclude={"tenant_id"})
        logger.debug(f"Prepared prompt data for processing: {prompt_data}")
        
        # Initialize pre-made prompts client and create PreMadePrompt instance
        try:
            logger.info("Initializing PreMadePromptsClient for connector operation")
            client = PreMadePromptsClient()
            pre_made_prompt = PreMadePrompt(**prompt_data)
            logger.info(f"Created PreMadePrompt instance for '{request.name}'")
            
            # Send to pre-made prompts service first
            try:
                logger.info(f"Sending prompt '{request.name}' to pre-made prompts service via connector...")
                await client.post_pre_made_prompt(pre_made_prompt)
                logger.info(f"Successfully sent prompt '{request.name}' to pre-made prompts service")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from pre-made prompts service: {e.response.status_code} - {e.response.text}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Pre-made prompts service error: {e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(f"Network error connecting to pre-made prompts service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Pre-made prompts service is unavailable"
                )
            except ValueError as e:
                logger.error(f"Validation error for pre-made prompt: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid prompt data: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Unexpected error with pre-made prompts service: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing prompt in service: {str(e)}"
                )
        except Exception as e:
            logger.error(f"Error initializing pre-made prompts client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize pre-made prompts client: {str(e)}"
            )
        
        # Create content for embedding after successful service update
        content = f"Prompt name: {prompt_data.get('name', '')}\n"
        content += f"Prompt body: {prompt_data.get('prompt_body', '')}\n"
        content += f"Associated tool: {prompt_data.get('associated_tool', '')}\n"
        content += f"Prompting technique: {prompt_data.get('prompting_technique', '')}\n"
        content += f"Concrete tasks: {', '.join(prompt_data.get('concrete_tasks', []))}\n"
        content += f"Placeholders: {', '.join(prompt_data.get('placeholders', []))}\n"
        content += f"Model compatibility: {', '.join(prompt_data.get('model_compatibility', []))}\n"
        
        # Add taxonomy info
        taxonomy = prompt_data.get('taxonomy', {})
        content += f"Department: {taxonomy.get('department', '')}\n"
        content += f"Team task category: {taxonomy.get('team_task_category', '')}\n"
        content += f"Type category: {taxonomy.get('type_category', '')}\n"
        
        # Add target audience info
        target_audience = prompt_data.get('target_audience', {})
        content += f"Expertise level: {target_audience.get('expertise_level', '')}\n"
        content += f"Job roles: {', '.join(target_audience.get('job_roles', []))}\n"
        
        # Add KPI benefits info
        kpi_benefits = prompt_data.get('kpi_benefits', {})
        if kpi_benefits:
            content += f"\nKPI Benefits:\n"
            if kpi_benefits.get('estimated_time_saving'):
                content += f"- Estimated time saving: {kpi_benefits['estimated_time_saving']}\n"
            if kpi_benefits.get('efficiency_gain_percentage'):
                content += f"- Efficiency gain: {kpi_benefits['efficiency_gain_percentage']}%\n"
            if kpi_benefits.get('cost_reduction'):
                content += f"- Cost reduction: {kpi_benefits['cost_reduction']}\n"
            if kpi_benefits.get('quality_improvement_metric'):
                content += f"- Quality improvement: {kpi_benefits['quality_improvement_metric']}\n"
        
        logger.info("Prompt data successfully processed by service, proceeding with local ingestion")
        
        # Validate required fields
        if not prompt_data.get('name'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt name is required"
            )
            
        if not prompt_data.get('prompt_body'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt body is required"
            )
            
        if not prompt_data.get('associated_tool'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Associated tool is required"
            )
        
        # Prepare input data
        input_data = {
            "content": content,
            "metadata": {
                "name": request.name,
                "prompt_body": request.prompt_body,
                "placeholders": request.placeholders,
                "associated_tool": request.associated_tool,
                "concrete_tasks": request.concrete_tasks,
                "taxonomy": request.taxonomy.model_dump(),
                "target_audience": request.target_audience.model_dump(),
                "kpi_benefits": request.kpi_benefits.model_dump(),
                "model_compatibility": request.model_compatibility,
                "prompting_technique": request.prompting_technique,
                "tags": request.tags,
                "document_type": "pre_made_prompt"
            },
            "job_id": job_id,
            "source_type": "pre_made_prompt"
        }
        
        logger.info("=" * 80)
        logger.info("Prepared input data for ingestion graph:")
        logger.info(f"Content length: {len(content)} characters")
        logger.info(f"Metadata fields: {list(input_data['metadata'].keys())}")
        logger.info("=" * 80)
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id="Pre Made Prompts"  # Use Pre Made Prompts tenant for global knowledge
        )
        
        if isinstance(result, Exception):
            logger.error(f"Error ingesting pre-made prompt: {str(result)}")
            logger.error("=" * 80)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest pre-made prompt: {str(result)}",
            )
            
        logger.info("=" * 80)
        logger.info(f"✓ Pre-made prompt ingestion completed with job ID: {job_id}")
        logger.info(f"✓ Prompt Name: {request.name}")
        logger.info(f"✓ Associated Tool: {request.associated_tool}")
        logger.info(f"✓ Data successfully sent to:")
        logger.info(f"  - Pre-Made Prompts Service (connector)")
        logger.info(f"  - Weaviate (Pre_Made_Prompts class)")
        logger.info(f"  - Neo4j (PreMadePrompt node + relationships)")
        logger.info("=" * 80)
        logger.info("=== PRE-MADE PROMPT INGESTION COMPLETED ===")
        logger.info("=" * 80)
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="Pre-made prompt ingestion started successfully"
        )
         
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"Error ingesting pre-made prompt: {str(e)}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest pre-made prompt: {str(e)}",
        ) from e


@router.post("/ingest/tenant-file", response_model=IngestResponse, tags=["ingestion"])
async def ingest_tenant_file(
    file: UploadFile = File(...),
    organization_id: str = None,
    tenant_id: str = "default",
    file_tags: str = None,  # Comma-separated tags
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)] = None,
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("tenant_file_ingestion_graph"))] = None,
):
    """
    Ingest Tenant File: Process and store content from an uploaded file for a specific organization.
    
    This endpoint handles tenant-specific file uploads, storing them in a way that allows
    for organization-specific retrieval and semantic search.
    """
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organization_id is required for tenant file uploads",
        )
        
    logger.info(f"Starting tenant file ingestion for organization {organization_id}: {file.filename}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    
    try:
        # Create a temporary file to store the uploaded content
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_path = temp_file.name
            
            # Write uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        try:
            # Parse tags if provided
            tags = []
            if file_tags:
                tags = [tag.strip() for tag in file_tags.split(",") if tag.strip()]
            
            # Prepare metadata for tenant uploaded file
            metadata = {
                "file_name": file.filename,
                "file_path": f"gs://tenant-files/{organization_id}/{file.filename}",  # Example GCS path
                "organization_id": organization_id,
                "file_type": os.path.splitext(file.filename)[1].lower(),
                "content_type": file.content_type,
                "file_size": len(content),
                "tags": tags,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "document_type": "tenant_uploaded_file"
            }
                
            # Prepare input data
            input_data = {
                "file_path": temp_path,
                "metadata": metadata,
                "job_id": job_id,
                "source_type": "tenant_uploaded_file",
                "filename": file.filename,
                "organization_id": organization_id  # Add organization_id to the top level
            }
            
            # Debug logging
            logger.info(f"Tenant file ingestion input_data: {input_data}")
            
            # Start async ingestion
            try:
                result = await ingestion_graph.ingest_document_async(
                    input_data=input_data,
                    tenant_id=tenant_id
                )
            except Exception as e:
                logger.error(f"Error in ingestion_graph.ingest_document_async: {str(e)}", exc_info=True)
                raise
            
            if isinstance(result, Exception):
                logger.error(f"Error ingesting tenant file: {str(result)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to ingest tenant file: {str(result)}",
                )
                
            logger.info(f"Tenant file ingestion started with job ID: {job_id}")
            
            # Return job ID with status information
            return IngestResponse(
                job_id=job_id,
                status_code=200,
                status_message="Tenant file ingestion started successfully"
            )
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error ingesting tenant file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest tenant file: {str(e)}",
        ) from e


@router.post("/ingest/gcs-file", response_model=IngestResponse, tags=["ingestion"])
async def ingest_gcs_file(
    request: GCSFileIngestionRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("gcs_file_ingestion_graph"))],
):
    """
    Ingest GCS File: Fetch a file from Google Cloud Storage, extract its text, and process it.
    
    This endpoint simulates the fetch_and_extract_text node in SynthDrive's LangGraph ingestion pipeline.
    It retrieves the file from GCS using the gcs_path and extracts raw text using an appropriate parser.
    """
    logger.info(f"Starting GCS file ingestion for organization {request.organization_id}: {request.gcs_path}")
    
    # Generate job ID for tracking
    job_id = str(uuid4())
    
    try:
        # Prepare initial state for the ingestion graph
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "gcs_path": request.gcs_path,
            "raw_text": None,
            "chunks": [],
            "entities_and_relations": [],
            "status": "pending",
            "processing_log": [f"Ingestion started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id,
            "job_id": job_id
        }
        
        # Add any additional metadata
        if request.metadata:
            initial_state["metadata"] = request.metadata
        
        try:
            # Start async ingestion
            logger.info(f"Starting ingestion with initial state: {initial_state}")
            result = await ingestion_graph.graph.ainvoke(initial_state)
            logger.info(f"Ingestion result: {result}")
            
            if isinstance(result, Exception):
                logger.error(f"Error ingesting GCS file: {str(result)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to ingest GCS file: {str(result)}",
                )
                
            if result.get("error"):
                logger.error(f"Error in ingestion graph: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to ingest GCS file: {result['error']}",
                )
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Unexpected error in GCS file ingestion: {str(e)}")
            logger.error(f"Traceback: {error_traceback}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ingest GCS file: {str(e)}\nTraceback: {error_traceback}",
            )
            
        logger.info(f"GCS file ingestion started with job ID: {job_id}")
        
        # Return job ID with status information
        return IngestResponse(
            job_id=job_id,
            status_code=200,
            status_message="GCS file ingestion started successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting GCS file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest GCS file: {str(e)}",
        ) from e


@router.post("/ingest/chunk-text", response_model=ChunkTextResponse, tags=["ingestion"])
async def chunk_text_api(
    request: ChunkTextRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Chunk Text: Apply a semantic chunking algorithm to break raw text into meaningful paragraphs or chunks.
    
    This endpoint implements the chunk_text node in SynthDrive's LangGraph ingestion flow.
    It takes raw text and applies semantic chunking to create meaningful chunks.
    """
    logger.info(f"Starting semantic chunking for file {request.file_id} in organization {request.organization_id}")
    
    try:
        # Prepare initial state for the chunking
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "raw_text": request.raw_text,
            "gcs_path": request.gcs_path,
            "chunks": [],
            "status": request.status,
            "processing_log": request.processing_log or [f"Chunking started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id
        }
        
        # Import the chunk_text function from nodes
        from src.ingestion.nodes import chunk_text
        
        # Apply the chunking algorithm
        result = chunk_text(initial_state)
        
        if result.get("status") == "failed":
            error_msg = "Failed to chunk text"
            if result.get("processing_log"):
                error_msg = result.get("processing_log")[-1]
            logger.error(f"Error in chunking text: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to chunk text: {error_msg}",
            )
        
        # Create response
        response = ChunkTextResponse(
            file_id=result.get("file_id"),
            organization_id=result.get("organization_id"),
            chunks=result.get("chunks", []),
            status=result.get("status", "chunked"),
            processing_log=result.get("processing_log", [])
        )
        
        # Ensure all metadata fields are preserved in the response
        for i, chunk in enumerate(response.chunks):
            if "metadata" in chunk:
                # Make sure chunk_id and chunk_index are set as integers, not empty strings
                chunk["metadata"]["chunk_id"] = i if chunk["metadata"].get("chunk_id") == "" else int(chunk["metadata"].get("chunk_id", i))
                chunk["metadata"]["chunk_index"] = i if chunk["metadata"].get("chunk_index") == "" else int(chunk["metadata"].get("chunk_index", i))
                
                # Make sure gcs_path is included
                if "gcs_path" not in chunk["metadata"] or chunk["metadata"]["gcs_path"] == "":
                    chunk["metadata"]["gcs_path"] = result.get("gcs_path", "")
        
        logger.info(f"Successfully chunked text for file {request.file_id}, created {len(response.chunks)} chunks")
        
        return response
        
    except Exception as e:
        logger.error(f"Error chunking text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chunk text: {str(e)}",
        ) from e
@router.post("/ingest/generate-embeddings", response_model=GenerateEmbeddingsResponse, tags=["ingestion"])
async def generate_embeddings_api(
    request: GenerateEmbeddingsRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Generate Embeddings: Generate vector embeddings for each text chunk.
    
    This endpoint implements the generate_embeddings node in SynthDrive's LangGraph ingestion flow.
    It takes text chunks and generates vector embeddings for each chunk.
    """
    logger.info(f"Starting embedding generation for file {request.file_id} in organization {request.organization_id}")
    
    try:
        # Prepare initial state for the embedding generation
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "chunks": request.chunks,
            "status": request.status,
            "processing_log": request.processing_log or [f"Embedding generation started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id
        }
        
        # Import the generate_embeddings function from nodes
        from src.ingestion.nodes import generate_embeddings
        
        # Apply the embedding generation algorithm
        result = generate_embeddings(initial_state)
        
        if result.get("status") == "failed":
            error_msg = "Failed to generate embeddings"
            if result.get("processing_log"):
                error_msg = result.get("processing_log")[-1]
            logger.error(f"Error in generating embeddings: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate embeddings: {error_msg}",
            )
        
        # Create response
        response = GenerateEmbeddingsResponse(
            file_id=result.get("file_id"),
            organization_id=result.get("organization_id"),
            chunks=result.get("chunks", []),
            status=result.get("status", "embedded"),
            processing_log=result.get("processing_log", [])
        )
        
        logger.info(f"Successfully generated embeddings for file {request.file_id}, processed {len(response.chunks)} chunks")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}",
        ) from e
@router.post("/ingest/extract-entities-relations", tags=["ingestion"])
async def extract_entities_and_relations(
    request: ChunkTextRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Extract Entities and Relations: Use an LLM for Named Entity Recognition (NER) and relationship extraction on the text.
    
    This endpoint implements the extract_entities_and_relations node in SynthDrive's LangGraph ingestion flow.
    It takes raw text or chunks and identifies entities like people, projects, tools, and their relations.
    """
    logger.info(f"Starting entity and relation extraction for file {request.file_id} in organization {request.organization_id}")
    
    try:
        # Prepare initial state for entity extraction
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "raw_text": request.raw_text,
            "chunks": [],
            "entities_and_relations": [],
            "status": request.status,
            "processing_log": request.processing_log or [f"Entity extraction started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id
        }
        
        # First, chunk the text if raw_text is provided but no chunks exist
        if request.raw_text and not initial_state["chunks"]:
            # Import the chunk_text function from nodes
            from src.ingestion.nodes import chunk_text
            
            # Apply the chunking algorithm
            chunked_state = chunk_text(initial_state)
            
            if chunked_state.get("status") == "failed":
                error_msg = "Failed to chunk text for entity extraction"
                if chunked_state.get("processing_log"):
                    error_msg = chunked_state.get("processing_log")[-1]
                logger.error(f"Error in chunking text: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to chunk text: {error_msg}",
                )
            
            # Update state with chunks
            initial_state["chunks"] = chunked_state.get("chunks", [])
            initial_state["processing_log"].append("Text chunked successfully for entity extraction")
        
        # Import the extract_entities function from nodes
        from src.ingestion.nodes import extract_entities
        
        # Extract processed_chunks from the state
        processed_chunks = []
        for chunk in initial_state.get("chunks", []):
            processed_chunks.append({
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {})
            })
        
        # Apply the entity extraction algorithm
        result = extract_entities(processed_chunks, initial_state.get("tenant_id", "default"))
        
        # Update the state with extracted entities and relations
        initial_state["entities_and_relations"] = result.get("entities", {})
        initial_state["status"] = "entities_extracted"
        initial_state["processing_log"].append(f"Entity extraction completed at {datetime.now(timezone.utc).isoformat()}")
        
        # Create response
        response = {
            "file_id": initial_state.get("file_id"),
            "organization_id": initial_state.get("organization_id"),
            "entities_and_relations": initial_state.get("entities_and_relations", {}),
            "status": initial_state.get("status", "entities_extracted"),
            "processing_log": initial_state.get("processing_log", [])
        }
        
        logger.info(f"Successfully extracted entities and relations for file {request.file_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error extracting entities and relations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract entities and relations: {str(e)}",
        ) from e


@router.post("/ingest/persist-to-weaviate", response_model=PersistToWeaviateResponse, tags=["ingestion"])
async def persist_to_weaviate_api(
    request: PersistToWeaviateRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Persist to Weaviate: Batch-insert embedded chunks into the tenant-specific Weaviate class.
    
    This endpoint implements the persist_to_weaviate node in SynthDrive's LangGraph ingestion flow.
    It takes chunks with embeddings and persists them to Weaviate with retry logic for errors.
    """
    logger.info(f"Starting Weaviate persistence for file {request.file_id} in organization {request.organization_id}")
    
    try:
        # Prepare initial state for Weaviate persistence
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "chunks": request.chunks,
            "status": request.status,
            "processing_log": request.processing_log or [f"Weaviate persistence started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id
        }
        
        # Import the persist_to_weaviate function from nodes
        from src.ingestion.nodes import persist_to_weaviate
        
        # Apply the Weaviate persistence function
        result = persist_to_weaviate(initial_state)
        
        if result.get("status") == "failed":
            error_msg = "Failed to persist to Weaviate"
            if result.get("processing_log"):
                error_msg = result.get("processing_log")[-1]
            logger.error(f"Error in persisting to Weaviate: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist to Weaviate: {error_msg}",
            )
        
        # Create response
        response = PersistToWeaviateResponse(
            file_id=result.get("file_id"),
            organization_id=result.get("organization_id"),
            status=result.get("status", "weaviate_persisted"),
            processing_log=result.get("processing_log", [])
        )
        
        logger.info(f"Successfully persisted chunks to Weaviate for file {request.file_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error persisting to Weaviate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist to Weaviate: {str(e)}",
        ) from e


@router.post("/ingest/persist-to-neo4j", response_model=PersistToNeo4jResponse, tags=["ingestion"])
async def persist_to_neo4j_api(
    request: PersistToNeo4jRequest,
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[IngestionGraph, Depends(get_ingestion_graph("document_ingestion_graph"))],
):
    """
    Persist to Neo4j: Translate extracted entities and relations into Cypher queries to create nodes and edges in Neo4j.
    
    This endpoint implements the persist_to_neo4j node in SynthDrive's LangGraph ingestion flow.
    It takes entities and relations and persists them to Neo4j, creating document nodes, entity nodes, and relationships.
    """
    logger.info(f"Starting Neo4j persistence for file {request.file_id} in organization {request.organization_id}")
    
    try:
        # Prepare initial state for Neo4j persistence
        initial_state = {
            "file_id": request.file_id,
            "organization_id": request.organization_id,
            "entities_and_relations": request.entities_and_relations,
            "status": request.status,
            "processing_log": request.processing_log or [f"Neo4j persistence started at {datetime.now(timezone.utc).isoformat()}"],
            "tenant_id": request.tenant_id
        }
        
        # Import the persist_to_neo4j function from nodes
        from src.ingestion.nodes import persist_to_neo4j
        
        # Apply the Neo4j persistence function
        result = persist_to_neo4j(initial_state)
        
        if result.get("status") == "failed":
            error_msg = "Failed to persist to Neo4j"
            if result.get("processing_log"):
                error_msg = result.get("processing_log")[-1]
            logger.error(f"Error in persisting to Neo4j: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist to Neo4j: {error_msg}",
            )
        
        # Create response
        response = PersistToNeo4jResponse(
            file_id=result.get("file_id"),
            organization_id=result.get("organization_id"),
            status=result.get("status", "neo4j_persisted"),
            processing_log=result.get("processing_log", [])
        )
        
        logger.info(f"Successfully persisted entities and relationships to Neo4j for file {request.file_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error persisting to Neo4j: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist to Neo4j: {str(e)}",
        ) from e