
from typing import Dict, List, Any, Optional, Tuple, Union
from uuid import uuid4
import logging
from datetime import datetime, timezone
import re
import os
import json
import asyncio
from pathlib import Path
import tempfile
import io
import requests
# Mock GCS functionality since the library is not available
# from google.cloud import storage

from openai import OpenAI
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredFileLoader,
    PyMuPDFLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient

# Configure logging
logger = logging.getLogger(__name__)


def load_document(input_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """
    Load and parse a document using LangChain loaders.
    
    Args:
        input_data: Dictionary containing file path or content and metadata
        tenant_id: The tenant ID for multi-tenancy
        
    Returns:
        Dictionary with processed document content and metadata
    """
    logger.info(f"Loading document for tenant {tenant_id}")
    
    try:
        # Check if input is a file path or direct content
        if "file_path" in input_data:
            file_path = input_data["file_path"]
            file_extension = Path(file_path).suffix.lower()
            
            # Select the appropriate loader based on file extension
            if file_extension == ".pdf":
                logger.info(f"Loading PDF document: {file_path}")
                loader = PyPDFLoader(file_path)
            elif file_extension == ".txt":
                logger.info(f"Loading text document: {file_path}")
                loader = TextLoader(file_path)
            elif file_extension == ".csv":
                logger.info(f"Loading CSV document: {file_path}")
                loader = CSVLoader(file_path)
            else:
                # Use a generic loader for other file types
                logger.info(f"Loading document with generic loader: {file_path}")
                loader = UnstructuredFileLoader(file_path)
            
            # Load the document
            documents = loader.load()
            
            # Extract metadata from the file
            metadata = input_data.get("metadata", {})
            metadata["source"] = file_path
            metadata["file_type"] = file_extension
            
            # Create a single document with all content
            content = "\n\n".join([doc.page_content for doc in documents])
            
        elif "content" in input_data:
            # Direct content input
            content = input_data["content"]
            metadata = input_data.get("metadata", {})
            
            if "source" not in metadata:
                metadata["source"] = "direct_input"
        else:
            raise ValueError("Input must contain either 'file_path' or 'content'")
        
        # Ensure metadata has required fields
        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # DON'T add tenant_id to metadata here - it will be added as a separate field in Weaviate
        # This prevents duplication where tenant_id appears both in metadata JSON and as a top-level field
        
        # Generate a document ID
        document_id = str(uuid4())
        metadata["document_id"] = document_id

        # Handle different document types
        document_type = metadata.get("document_type")
        source_type = input_data.get("source_type", "")
        
        logger.info(f"load_document: document_type={document_type}, source_type={source_type}")
        
        # Handle global knowledge domain data first
        if source_type in ["global_tool", "global_learning_resource", "global_ecosystem_partner", "no_code_template", "pre_made_prompt"]:
            logger.info(f"Processing {source_type} data")
            
            # For global AI tools, learning resources, ecosystem partners, and no-code templates
            # The content is already prepared in the endpoint
            if source_type == "global_tool":
                metadata["tool_id"] = metadata.get("tool_id", str(uuid4()))
                logger.info(f"Processing global tool with document_type: {document_type}, source_type: {source_type}")
                # Ensure document_type is set correctly for global tools
                if document_type != "global_tool":
                    logger.warning(f"Document type mismatch for global tool: {document_type}. Setting to 'global_tool'")
                    metadata["document_type"] = "global_tool"
            elif source_type == "global_learning_resource":
                metadata["resource_id"] = metadata.get("resource_id", str(uuid4()))
                metadata["source_type"] = "global_learning_resource"
                logger.info(f"Processing global learning resource with ID: {metadata['resource_id']}")
                logger.info(f"Learning resource metadata: {metadata}")
            elif source_type == "global_ecosystem_partner":
                metadata["partner_id"] = metadata.get("partner_id", str(uuid4()))
                logger.info(f"Processing global ecosystem partner with document_type: {document_type}, source_type: {source_type}")
                # Ensure document_type is set correctly for ecosystem partners
                if document_type != "ecosystem_partner":
                    logger.warning(f"Document type mismatch for ecosystem partner: {document_type}. Setting to 'ecosystem_partner'")
                    metadata["document_type"] = "ecosystem_partner"
                
                # Ensure source_type is preserved in metadata
                metadata["source_type"] = "global_ecosystem_partner"
                logger.info(f"Updated metadata for ecosystem partner: {metadata}")
            elif source_type == "no_code_template":
                metadata["template_id"] = metadata.get("template_id", str(uuid4()))
                logger.info(f"Processing no-code template with document_type: {document_type}, source_type: {source_type}")
                # Ensure document_type is set correctly for no-code templates
                if document_type != "no_code_template":
                    logger.warning(f"Document type mismatch for no-code template: {document_type}. Setting to 'no_code_template'")
                    metadata["document_type"] = "no_code_template"
                
                # Ensure source_type is preserved in metadata
                metadata["source_type"] = "no_code_template"
                logger.info(f"Updated metadata for no-code template: {metadata}")
            elif source_type == "pre_made_prompt":
                metadata["prompt_id"] = metadata.get("prompt_id", str(uuid4()))
                logger.info(f"Processing pre-made prompt with document_type: {document_type}, source_type: {source_type}")
                # Ensure document_type is set correctly for pre-made prompts
                if document_type != "pre_made_prompt":
                    logger.warning(f"Document type mismatch for pre-made prompt: {document_type}. Setting to 'pre_made_prompt'")
                    metadata["document_type"] = "pre_made_prompt"
                
                # Ensure source_type is preserved in metadata
                metadata["source_type"] = "pre_made_prompt"
                logger.info(f"Updated metadata for pre-made prompt: {metadata}")
        
        # Handle tenant uploaded files
        elif source_type == "tenant_uploaded_file":
            logger.info(f"Processing tenant uploaded file data")
            logger.info(f"Input data: {input_data}")
            logger.info(f"Initial metadata: {metadata}")
            
            # Ensure organization_id is set
            if "organization_id" not in metadata and "organization_id" not in input_data:
                logger.error(f"Missing organization_id in both metadata and input_data")
                raise ValueError("organization_id is required for tenant uploaded files")
            
            # Copy organization_id from input_data to metadata if not in metadata
            if "organization_id" not in metadata and "organization_id" in input_data:
                logger.info(f"Copying organization_id from input_data: {input_data['organization_id']}")
                metadata["organization_id"] = input_data["organization_id"]
            
            # Set file_id if not provided
            metadata["file_id"] = metadata.get("file_id", str(uuid4()))
            
            # Set file_type if not provided but can be inferred from file_path
            if "file_type" not in metadata and "file_path" in metadata:
                file_path = metadata["file_path"]
                file_extension = Path(file_path).suffix.lower()
                metadata["file_type"] = file_extension
            
            # Set document_type for tenant uploaded files
            metadata["document_type"] = "tenant_uploaded_file"
            metadata["source_type"] = "tenant_uploaded_file"
        
        # Handle regular tool data (not global)
        elif document_type == "tool":
            # Assume content is JSON string of tool data
            try:
                tool_data = json.loads(content)
                # Store in Postgres
                postgres_client = PostgresClient(settings.POSTGRES_URI)
                tool_id = postgres_client.add_tool(tool_data, tenant_id)
                # Generate embeddable content
                content = f"Tool name: {tool_data.get('name', '')}\nDescription: {tool_data.get('description', '')}\nUse case: {tool_data.get('use_case', '')}\nReviews: {tool_data.get('reviews', '')}"
                metadata["tool_id"] = tool_id
                logger.info(f"Processed tool data for embedding with tool_id: {tool_id}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON for tool content: {str(e)}")
                raise ValueError("Tool content must be valid JSON.")
                

        logger.info(f"Successfully loaded document with ID {document_id}")
        
        return {
            "input_data": {
                "content": content,
                "metadata": metadata,
                "source_type": source_type
            }
        }
    except Exception as e:
        logger.error(f"Error loading document: {str(e)}")
        raise


def chunk_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a semantic chunking algorithm to break the raw text into meaningful paragraphs or chunks.
    
    Args:
        state: The current state containing raw_text and other fields
        
    Returns:
        Updated state with chunks field populated
    """
    logger.info("Applying semantic chunking to raw text")
    
    try:
        # Initialize state if not present
        if 'status' not in state:
            state['status'] = 'processing'
        if 'processing_log' not in state:
            state['processing_log'] = []
        if 'chunks' not in state:
            state['chunks'] = []
            
        # Update status
        state['processing_log'].append(f"Started semantic chunking at {datetime.now(timezone.utc).isoformat()}")
        
        # Get the raw text
        raw_text = state.get('raw_text')
        if not raw_text:
            error_msg = "No raw text available for chunking"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Initialize OpenAI client
        api_key = settings.OPENAI_API_KEY
        
        # Configure the OpenAI client with additional options
        client_kwargs = {
            "api_key": api_key,
        }
        
        # Add organization if available
        if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
            client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
            
        # Create the client
        client = OpenAI(**client_kwargs)
        
        # First, use a simple paragraph-based chunking as a fallback
        # Split by double newlines (paragraphs)
        simple_chunks = re.split(r'\n\s*\n', raw_text)
        simple_chunks = [chunk.strip() for chunk in simple_chunks if chunk.strip()]
        
        # For very short texts, just use simple chunking
        if len(raw_text) < 1000 or len(simple_chunks) <= 3:
            logger.info(f"Text is short, using simple paragraph-based chunking: {len(simple_chunks)} chunks")
            
            # Create chunks with metadata
            for i, chunk_text in enumerate(simple_chunks):
                # Generate a unique ID for each chunk
                chunk_id = i + 1  # Start from 1 instead of 0
                chunk = {
                    "content": chunk_text,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "chunk_type": "paragraph",
                        "semantic_type": "auto-detected",
                        "chunk_index": i + 1,  # Start from 1 instead of 0
                        "total_chunks": len(simple_chunks),
                        "file_id": state.get("file_id", ""),
                        "organization_id": state.get("organization_id", ""),
                        "gcs_path": state.get("gcs_path", ""),
                        "chunking_method": "simple_paragraph"
                    }
                }
                state['chunks'].append(chunk)
                
            state['processing_log'].append(f"Created {len(simple_chunks)} chunks using simple paragraph-based chunking")
            state['status'] = 'chunked'
            return state
        
        # For longer texts, use AI to identify semantic chunks
        # Create a prompt for semantic chunking
        prompt = f"""
        You are an expert at semantic chunking of documents. Your task is to break the following text into meaningful, 
        semantically coherent chunks. Each chunk should represent a complete thought, concept, or section.
        
        Guidelines for chunking:
        1. Each chunk should be semantically coherent and self-contained when possible
        2. Identify natural section breaks, topic transitions, and semantic boundaries
        3. Preserve the context and meaning of the original text
        4. Label each chunk with an appropriate semantic type (e.g., introduction, concept explanation, example, conclusion)
        5. Keep chunks to a reasonable size (roughly 200-1000 characters)
        
        Return the chunks as a JSON array where each object has:
        - "content": The text content of the chunk
        - "semantic_type": A label describing the semantic function of this chunk
        
        Here is the text to chunk:
        
        {raw_text[:5000]}  # Limit to first 5000 chars for API limits
        
        JSON:
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Using a capable model for semantic analysis
            messages=[
                {"role": "system", "content": "You are an expert semantic chunking system. Break text into meaningful, semantically coherent chunks and return them in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result = response.choices[0].message.content
        
        try:
            # Extract the chunks
            chunking_result = json.loads(result)
            ai_chunks = chunking_result.get("chunks", [])
            
            # If AI chunking failed or returned no chunks, fall back to simple chunking
            if not ai_chunks:
                logger.warning("AI chunking returned no chunks, falling back to simple chunking")
                
                # Use the simple chunks we already created
                for i, chunk_text in enumerate(simple_chunks):
                    # Generate a unique ID for each chunk
                    chunk_id = i + 1  # Start from 1 instead of 0
                    chunk = {
                        "content": chunk_text,
                        "metadata": {
                            "chunk_id": chunk_id,
                            "chunk_type": "paragraph",
                            "semantic_type": "auto-detected",
                            "chunk_index": i + 1,  # Start from 1 instead of 0
                            "total_chunks": len(simple_chunks),
                            "file_id": state.get("file_id", ""),
                            "organization_id": state.get("organization_id", ""),
                            "gcs_path": state.get("gcs_path", ""),
                            "chunking_method": "simple_paragraph_fallback"
                        }
                    }
                    state['chunks'].append(chunk)
            else:
                # Process AI-generated chunks
                for i, chunk_data in enumerate(ai_chunks):
                    # Generate a unique ID for each chunk
                    chunk_id = i + 1  # Start from 1 instead of 0
                    chunk = {
                        "content": chunk_data.get("content", ""),
                        "metadata": {
                            "chunk_id": chunk_id,
                            "chunk_type": "semantic",
                            "semantic_type": chunk_data.get("semantic_type", "unknown"),
                            "chunk_index": i + 1,  # Start from 1 instead of 0
                            "total_chunks": len(ai_chunks),
                            "file_id": state.get("file_id", ""),
                            "organization_id": state.get("organization_id", ""),
                            "gcs_path": state.get("gcs_path", ""),
                            "chunking_method": "ai_semantic"
                        }
                    }
                    state['chunks'].append(chunk)
                
                logger.info(f"Created {len(ai_chunks)} chunks using AI semantic chunking")
                state['processing_log'].append(f"Created {len(ai_chunks)} chunks using AI semantic chunking")
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse AI chunking result as JSON: {result}")
            logger.warning("Falling back to simple paragraph-based chunking")
            
            # Use the simple chunks we already created
            for i, chunk_text in enumerate(simple_chunks):
                # Generate a unique ID for each chunk
                chunk_id = i + 1  # Start from 1 instead of 0
                chunk = {
                    "content": chunk_text,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "chunk_type": "paragraph",
                        "semantic_type": "auto-detected",
                        "chunk_index": i + 1,  # Start from 1 instead of 0
                        "total_chunks": len(simple_chunks),
                        "file_id": state.get("file_id", ""),
                        "organization_id": state.get("organization_id", ""),
                        "gcs_path": state.get("gcs_path", ""),
                        "chunking_method": "simple_paragraph_fallback"
                    }
                }
                state['chunks'].append(chunk)
            
            state['processing_log'].append(f"AI chunking failed, created {len(simple_chunks)} chunks using simple paragraph-based chunking")
        
        # Handle very long texts by processing the remainder
        if len(raw_text) > 5000:
            logger.info("Text is longer than 5000 chars, processing remainder with simple chunking")
            
            # Process the remainder with simple chunking
            remainder_text = raw_text[5000:]
            remainder_chunks = re.split(r'\n\s*\n', remainder_text)
            remainder_chunks = [chunk.strip() for chunk in remainder_chunks if chunk.strip()]
            
            # Add remainder chunks
            current_chunk_count = len(state['chunks'])
            for i, chunk_text in enumerate(remainder_chunks):
                # Generate a unique ID for each chunk
                chunk_id = current_chunk_count + i + 1  # Start from current_chunk_count + 1
                chunk = {
                    "content": chunk_text,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "chunk_type": "paragraph",
                        "semantic_type": "remainder",
                        "chunk_index": current_chunk_count + i + 1,  # Start from current_chunk_count + 1
                        "total_chunks": current_chunk_count + len(remainder_chunks),
                        "file_id": state.get("file_id", ""),
                        "organization_id": state.get("organization_id", ""),
                        "gcs_path": state.get("gcs_path", ""),
                        "chunking_method": "simple_paragraph_remainder"
                    }
                }
                state['chunks'].append(chunk)
            
            state['processing_log'].append(f"Added {len(remainder_chunks)} additional chunks from remainder text")
        
        # Update status
        state['status'] = 'chunked'
        state['processing_log'].append(f"Completed semantic chunking at {datetime.now(timezone.utc).isoformat()}")
        
        return state
    
    except Exception as e:
        logger.error(f"Unexpected error in chunk_text: {str(e)}")
        if 'processing_log' in state:
            state['processing_log'].append(f"Critical error in semantic chunking: {str(e)}")
        state['status'] = 'failed'
        return state


def chunk_and_embed(input_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """
    Chunk the document and create embeddings.
    
    Args:
        input_data: Dictionary containing document content and metadata
        tenant_id: The tenant ID for multi-tenancy
        
    Returns:
        Dictionary with processed chunks and embeddings
    """
    logger.info(f"Chunking and embedding document for tenant {tenant_id}")
    logger.info(f"Input data keys: {input_data.keys()}")
    
    try:
        # Validate input data
        if not input_data:
            logger.error(f"Invalid input data for chunking and embedding for tenant {tenant_id}")
            return {
                "processed_chunks": [],
                "embeddings": []
            }
            
        content = input_data.get("content", "")
        if not content:
            logger.warning(f"Empty content for chunking and embedding for tenant {tenant_id}")
            
            # Special handling for tenant uploaded files
            source_type = input_data.get("source_type", "")
            metadata = input_data.get("metadata", {})
            document_type = metadata.get("document_type", "")
            
            if source_type == "tenant_uploaded_file" or document_type == "tenant_uploaded_file":
                logger.info("This is a tenant uploaded file with empty content, creating a single chunk with metadata")
                
                # Create a single chunk with the metadata
                processed_chunks = [{
                    "content": "Empty content for tenant uploaded file",
                    "metadata": {
                        **metadata,
                        "chunk_id": 0,
                        # NOTE: tenant_id is NOT added here to avoid duplication
                        # It will be stored separately in Weaviate as a top-level field
                        "document_type": "tenant_uploaded_file",
                        "source_type": "tenant_uploaded_file"
                    }
                }]
                
                # Create a dummy embedding
                embeddings = [[0.0] * 1536]  # Standard OpenAI embedding size
                
                return {
                    "processed_chunks": processed_chunks,
                    "embeddings": embeddings
                }
            
            return {
                "processed_chunks": [],
                "embeddings": []
            }
            
        metadata = input_data.get("metadata", {})
        source_type = input_data.get("source_type", "")
        document_type = metadata.get("document_type", "")
        logger.info(f"chunk_and_embed: source_type from input_data: '{source_type}'")
        logger.info(f"chunk_and_embed: document_type from metadata: '{document_type}'")

        # Check if this is a global knowledge item that should not be chunked
        source_type_from_metadata = metadata.get("source_type", "")
        is_global_knowledge_item = (
            source_type in ["global_tool", "global_learning_resource", "global_ecosystem_partner"] or
            source_type_from_metadata in ["global_tool", "global_learning_resource", "global_ecosystem_partner"] or
            document_type in ["global_tool", "learning_resource", "ecosystem_partner"]
        )

        if is_global_knowledge_item:
            logger.info(f"Detected global knowledge item ({source_type}/{document_type}), treating as single chunk")
            # For global knowledge items, don't split into chunks - treat as single entity
            processed_chunks = [{
                "content": content,
                "metadata": {
                    **metadata,
                    "chunk_id": 0,
                    # NOTE: tenant_id is NOT added here to avoid duplication
                    # It will be stored separately in Weaviate as a top-level field
                    "source_type": source_type,
                    "document_type": document_type
                }
            }]
        else:
            # Create a text splitter for recursive chunking
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            # Split the text into chunks
            chunks = text_splitter.create_documents([content], [metadata])

            # Process chunks into a standard format
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = chunk.metadata.copy()
                chunk_metadata["chunk_id"] = i
                # NOTE: tenant_id is NOT added here to avoid duplication
                # It will be stored separately in Weaviate as a top-level field

                processed_chunks.append({
                    "content": chunk.page_content,
                    "metadata": chunk_metadata
                })
        
        logger.info(f"Created {len(processed_chunks)} chunks")
        
        # Initialize OpenAI embeddings
        api_key = settings.OPENAI_API_KEY
        
        embeddings_model = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=settings.EMBEDDING_MODEL,
            openai_organization=settings.OPENAI_ORGANIZATION if hasattr(settings, 'OPENAI_ORGANIZATION') else None
        )
        
        # Generate embeddings for all chunks
        texts = [chunk["content"] for chunk in processed_chunks]
        embeddings = embeddings_model.embed_documents(texts)
        
        logger.info(f"Generated embeddings with {len(embeddings[0])} dimensions")
        
        return {
            "processed_chunks": processed_chunks,
            "embeddings": embeddings
        }
    except Exception as e:
        logger.error(f"Error chunking and embedding document: {str(e)}")
        raise


def extract_entities(processed_chunks: List[Dict[str, Any]], tenant_id: str) -> Dict[str, Any]:
    """
    Extract entities and relationships from document chunks.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        tenant_id: The tenant ID for multi-tenancy
        
    Returns:
        Dictionary with extracted entities and relationships
    """
    logger.info(f"Extracting entities for tenant {tenant_id}")
    
    # Check if processed_chunks is None or empty
    if not processed_chunks:
        logger.warning(f"No processed chunks available for entity extraction for tenant {tenant_id}")
        return {"entities": {"entities": [], "relationships": []}}
        
    # Check if this is an ecosystem partner
    if processed_chunks and len(processed_chunks) > 0:
        first_chunk = processed_chunks[0]
        metadata = first_chunk.get("metadata", {})
        source_type = metadata.get("source_type", "")
        document_type = metadata.get("document_type", "")
        if source_type == "global_ecosystem_partner" or document_type == "ecosystem_partner":
            logger.info("Skipping entity extraction for global ecosystem partner")
            return {"entities": {"entities": [], "relationships": []}}
    
    try:
        # Initialize OpenAI client
        # Handle both standard and project-based API keys
        api_key = settings.OPENAI_API_KEY
        
        # Configure the OpenAI client with additional options
        client_kwargs = {
            "api_key": api_key,
        }
        
        # Add organization if available
        if hasattr(settings, 'OPENAI_ORGANIZATION') and settings.OPENAI_ORGANIZATION:
            client_kwargs["organization"] = settings.OPENAI_ORGANIZATION
            
        # Create the client without the project parameter
        client = OpenAI(**client_kwargs)
        
        all_entities = []
        
        # Process each chunk to extract entities
        for chunk in processed_chunks:
            content = chunk["content"]
            chunk_metadata = chunk["metadata"]
            
            # Create a prompt for entity and relationship extraction
            prompt = f"""
            Extract named entities and their relationships from the following text.
            Return a JSON object with two arrays:
            1. "entities": Each entity should have "name", "type", and "id" fields.
            2. "relationships": Each relationship should have "source_id", "target_id", "type", and "description" fields.
            
            Entity types should be one of: PERSON, ORGANIZATION, LOCATION, DATE, EVENT, PRODUCT, CONCEPT.
            Relationship types should be descriptive of the connection between entities.
            
            Text: {content}
            
            JSON:
            """
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o",  # Using a more capable model for entity extraction
                messages=[
                    {"role": "system", "content": "You are an expert entity and relationship extraction system. Extract named entities and their relationships from text and return them in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = response.choices[0].message.content
            
            try:
                # Extract the entities and relationships
                extraction_result = json.loads(result)
                
                # Add chunk metadata to entities
                for entity in extraction_result.get("entities", []):
                    entity["chunk_id"] = chunk_metadata.get("chunk_id")
                    entity["document_id"] = chunk_metadata.get("document_id")
                    entity["tenant_id"] = tenant_id
                
                # Add chunk metadata to relationships
                for relationship in extraction_result.get("relationships", []):
                    relationship["chunk_id"] = chunk_metadata.get("chunk_id")
                    relationship["document_id"] = chunk_metadata.get("document_id")
                    relationship["tenant_id"] = tenant_id
                
                all_entities.append(extraction_result)
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse entity extraction result as JSON: {result}")
                continue
        
        # Combine all entities and relationships
        combined_entities = []
        combined_relationships = []
        
        for result in all_entities:
            combined_entities.extend(result.get("entities", []))
            combined_relationships.extend(result.get("relationships", []))
        
        # Deduplicate entities by name and type
        unique_entities = {}
        for entity in combined_entities:
            key = f"{entity['name']}_{entity['type']}"
            if key not in unique_entities:
                unique_entities[key] = entity
        
        logger.info(f"Extracted {len(unique_entities)} unique entities and {len(combined_relationships)} relationships")
        
        return {
            "entities": {
                "entities": list(unique_entities.values()),
                "relationships": combined_relationships
            }
        }
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        # Return empty entities on error
        return {"entities": {"entities": [], "relationships": []}}


def route_to_stores(
    processed_chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    entities: Dict[str, Any],
    tenant_id: str
) -> Dict[str, Any]:
    """
    Determine which data stores to route the document to.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        embeddings: List of embeddings for each chunk
        entities: Dictionary with extracted entities and relationships
        tenant_id: The tenant ID for multi-tenancy
        
    Returns:
        Dictionary with destinations for routing
    """
    logger.info(f"===== ROUTE_TO_STORES: Starting routing for tenant {tenant_id} =====")
    logger.info(f"processed_chunks: {processed_chunks is not None}, embeddings: {embeddings is not None}, entities: {entities is not None}")
    
    if entities:
        logger.info(f"Entities structure: {list(entities.keys()) if isinstance(entities, dict) else type(entities)}")
        if isinstance(entities, dict) and 'entities' in entities:
            logger.info(f"Number of entities: {len(entities.get('entities', []))}")
            logger.info(f"Entity  list: {entities.get('entities', [])}")

    try:
        destinations = []
        
        # Check if this is a special global knowledge type
        is_global_tool = False
        is_ecosystem_partner = False
        
        if processed_chunks and len(processed_chunks) > 0:
            first_chunk = processed_chunks[0]
            metadata = first_chunk.get("metadata", {})
            source_type = metadata.get("source_type", "")
            document_type = metadata.get("document_type", "")
            
            # Log the metadata for debugging
            logger.info(f"route_to_stores: metadata={metadata}, source_type={source_type}, document_type={document_type}")
            
            if source_type == "global_tool" or document_type == "global_tool":
                is_global_tool = True
                logger.info("This is a global tool, routing to both Weaviate and Neo4j")
                destinations.append("weaviate")
                destinations.append("neo4j")
                
            elif source_type == "global_ecosystem_partner" or document_type == "ecosystem_partner":
                is_ecosystem_partner = True
                logger.info("This is a global ecosystem partner, routing to both Weaviate and Neo4j")
                destinations.append("weaviate")
                logger.info(f"Added Weaviate to destinations: {destinations}")

                # Add Neo4j routing for ecosystem partners to create graph
                # Ecosystem partners ALWAYS go to Neo4j, even without entities
                destinations.append("neo4j")
                logger.info(f"===== ADDED NEO4J TO DESTINATIONS for ecosystem partner =====")
                logger.info(f"Final destinations: {destinations}")
        
        # For non-special types, use the normal routing logic
        if not is_global_tool and not is_ecosystem_partner:
            # Check if we have valid processed_chunks and embeddings
            if processed_chunks and embeddings:
                # Always route to Weaviate for vector search
                destinations.append("weaviate")
            else:
                logger.warning(f"Missing processed_chunks or embeddings for tenant {tenant_id}. Cannot route to Weaviate.")
                # If we're missing chunks or embeddings but this is a tenant uploaded file, still route to Weaviate
                if processed_chunks and processed_chunks[0]["metadata"].get("document_type") == "tenant_uploaded_file":
                    logger.info("This is a tenant uploaded file, routing to Weaviate despite missing embeddings")
                    destinations.append("weaviate")
            
            # Route to Neo4j if entities were detected
            if entities and entities.get("entities") and len(entities.get("entities", [])) > 0:
                destinations.append("neo4j")
        
        logger.info(f"Routing to destinations: {destinations}")
        
        # Ensure we always have at least one destination
        if not destinations:
            logger.warning("No destinations determined, defaulting to Weaviate")
            destinations.append("weaviate")
        
        return {
            "destinations": destinations
        }
    except Exception as e:
        logger.error(f"Error routing to stores: {str(e)}", exc_info=True)
        # Default to Weaviate only on error
        return {"destinations": ["weaviate"]}


def store_in_weaviate(
    processed_chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    tenant_id: str,
    weaviate_client: WeaviateClient
) -> None:
    """
    Store document chunks and embeddings in Weaviate.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        embeddings: List of embeddings for each chunk
        tenant_id: The tenant ID for multi-tenancy
        weaviate_client: The Weaviate client
    """
    logger.info(f"Storing document chunks in Weaviate for tenant {tenant_id}")
    
    # Check if we have valid processed_chunks and embeddings
    if not processed_chunks or not embeddings:
        logger.warning(f"No processed chunks or embeddings to store in Weaviate for tenant {tenant_id}")
        return
        
    # Log the first chunk's metadata for debugging
    if processed_chunks and len(processed_chunks) > 0:
        first_chunk = processed_chunks[0]
        metadata = first_chunk.get("metadata", {})
        document_type = metadata.get("document_type", "")
        source_type = metadata.get("source_type", "")
        logger.info(f"store_in_weaviate: First chunk metadata: document_type={document_type}, source_type={source_type}")
        
    # Check if this is an ecosystem partner
    is_ecosystem_partner = False
    if processed_chunks and len(processed_chunks) > 0:
        first_chunk = processed_chunks[0]
        metadata = first_chunk.get("metadata", {})
        source_type = metadata.get("source_type", "")
        document_type = metadata.get("document_type", "")
        
        # Check both source_type in metadata and the input_data source_type
        if source_type == "global_ecosystem_partner" or document_type == "ecosystem_partner":
            is_ecosystem_partner = True
            logger.info("Detected ecosystem partner, will use specialized storage method")
    
    # For ecosystem partners, we only need the first chunk since we don't split them
    if is_ecosystem_partner and processed_chunks and len(processed_chunks) > 0:
        try:
            from src.core.security import validate_metadata
            
            chunk = processed_chunks[0]
            content = chunk["content"]
            metadata = chunk["metadata"]
            
            # Validate and ensure tenant isolation
            metadata = validate_metadata(metadata, tenant_id)
            
            # NOTE: Do NOT add tenant_id to metadata here to avoid duplication
            # The tenant_id will be passed separately to Weaviate methods
            # and stored as a top-level field, not in the metadata JSON
            
            # Debug logging
            logger.info(f"Ecosystem partner metadata: {metadata}")
            
            # Prepare partner data
            partner_data = {
                "name": metadata.get("name", ""),
                "bio": metadata.get("bio", ""),
                "expertise": metadata.get("expertise", []),
                "certifications": metadata.get("certifications", []),
                "case_studies": metadata.get("case_studies", ""),
                "website": metadata.get("website", ""),
                "contact_info": metadata.get("contact_info", ""),
                "budget_tier": metadata.get("budget_tier", ""),
                "partner_id": metadata.get("partner_id", str(uuid4())),
                "tags": metadata.get("tags", []),
                "content": content,
                "tenant_id": tenant_id
            }
            
            # Debug logging
            logger.info(f"Prepared partner data: {partner_data}")
            
            try:
                # Use the specialized method for ecosystem partners
                partner_id = weaviate_client.add_ecosystem_partner(partner_data, tenant_id)
                logger.info(f"Added ecosystem partner to Weaviate with ID: {partner_id}")
                
                # Verify the partner was added to Global_Ecosystem
                try:
                    result = weaviate_client.client.query.get(
                        "Global_Ecosystem",
                        ["name", "partner_id"]
                    ).with_where({
                        "path": ["partner_id"],
                        "operator": "Equal",
                        "valueString": partner_id
                    }).do()
                    
                    if result and "data" in result and "Get" in result["data"] and "Global_Ecosystem" in result["data"]["Get"]:
                        objects = result["data"]["Get"]["Global_Ecosystem"]
                        if objects:
                            logger.info(f"Successfully verified partner in Global_Ecosystem: {objects[0].get('name')}")
                        else:
                            logger.warning(f"Partner with ID {partner_id} not found in Global_Ecosystem after adding")
                    else:
                        logger.warning(f"Failed to verify partner in Global_Ecosystem: {result}")
                except Exception as verify_error:
                    logger.error(f"Error verifying partner in Global_Ecosystem: {str(verify_error)}")
            except Exception as add_error:
                logger.error(f"Error adding ecosystem partner to Weaviate: {str(add_error)}")
                # Don't raise here, let's try the generic method as fallback
                logger.info("Falling back to generic document storage method")
                # Continue with normal processing below
                return
            
            return  # Exit early since we've handled the ecosystem partner
        except Exception as e:
            logger.error(f"Error adding ecosystem partner to Weaviate: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    # Check if lengths match for regular documents
    if len(processed_chunks) != len(embeddings):
        logger.error(f"Mismatch between number of chunks ({len(processed_chunks)}) and embeddings ({len(embeddings)}) for tenant {tenant_id}")
        return
    
    try:
        from src.core.security import validate_metadata
        
        # Store each chunk with its embedding
        for i, (chunk, embedding) in enumerate(zip(processed_chunks, embeddings)):
            try:
                content = chunk["content"]
                metadata = chunk["metadata"]
                
                # Validate and ensure tenant isolation
                metadata = validate_metadata(metadata, tenant_id)
                
                # NOTE: Do NOT add tenant_id to metadata here to avoid duplication
                # The tenant_id will be passed separately to add_document method
                # and stored as a top-level field, not in the metadata JSON
                
                # Determine the appropriate class name based on document type
                document_type = metadata.get("document_type", "")
                source_type = metadata.get("source_type", "")
                
                if document_type == "tool" or document_type == "global_tool" or source_type == "global_tool":
                    # Use specialized method for global tools
                    logger.info(f"Storing in Global_Tools class. document_type: {document_type}, source_type: {source_type}")
                    logger.info(f"Tool metadata: {metadata}")
                    
                    # Prepare tool data from metadata
                    tool_data = {
                        "name": metadata.get("name", ""),
                        "homepage_url": metadata.get("homepage_url", ""),
                        "last_scraped_at": metadata.get("last_scraped_at", ""),
                        "source_urls": metadata.get("source_urls", []),
                        "categories": {
                            "primary": metadata.get("categories", {}).get("primary", "") if isinstance(metadata.get("categories", {}), dict) else "",
                            "secondary": metadata.get("categories", {}).get("secondary", []) if isinstance(metadata.get("categories", {}), dict) else []
                        },
                        "short_description": metadata.get("short_description", ""),
                        "detailed_description": metadata.get("detailed_description", ""),
                        "features": metadata.get("features", []),
                        "differentiators": metadata.get("differentiators", []),
                        "subscriptions": metadata.get("subscriptions", []),
                        "compliance": metadata.get("compliance", {}),
                        "documentation_links": metadata.get("documentation_links", []),
                        "rating": metadata.get("rating", 0.0),
                        "logo_url": metadata.get("logo_url", ""),
                        "tags": metadata.get("tags", [])
                    }
                    
                    # Use the specialized add_global_tool method
                    tool_id = weaviate_client.add_global_tool(tool_data, tenant_id)
                    logger.info(f"Added global tool to Weaviate with ID: {tool_id}")
                elif document_type == "learning_resource" or source_type == "global_learning_resource":
                    # Use specialized method for learning resources
                    logger.info(f"=== Storing Learning Resource in Weaviate ===")
                    logger.info(f"Storing in Global_LearningResources class. document_type: {document_type}, source_type: {source_type}")
                    logger.info(f"Learning resource details - Title: {metadata.get('title')}, Type: {metadata.get('resource_type')}")
                    logger.info(f"Learning resource categories: {metadata.get('categories', {})}")
                    logger.info(f"Learning resource topics: {metadata.get('topics_discussed', [])}")
                    logger.info(f"Full metadata being processed: {metadata}")
                    
                    # Prepare resource data from metadata - ensure all fields are included
                    logger.info(f"Metadata keys: {list(metadata.keys())}")
                    logger.info(f"Metadata platform_name: {metadata.get('platform_name')}")
                    logger.info(f"Metadata associated_tool: {metadata.get('associated_tool')}")
                    logger.info(f"Metadata taxonomy: {metadata.get('taxonomy')}")
                    logger.info(f"Metadata kpi_benefits: {metadata.get('kpi_benefits')}")
                    logger.info(f"Metadata subscriptions: {metadata.get('subscriptions')}")

                    resource_data = {
                        "title": metadata.get("title", ""),
                        "description": metadata.get("description", ""),
                        "source_url": metadata.get("source_url", ""),
                        "resource_type": metadata.get("resource_type", ""),
                        "categories": metadata.get("categories", {}),
                        "topics_discussed": metadata.get("topics_discussed", []),
                        "target_audience": metadata.get("target_audience", {}),
                        "useful_context": metadata.get("useful_context", []),
                        "content": metadata.get("content", {}),
                        "tags": metadata.get("tags", []),
                        "estimatedTime": metadata.get("estimatedTime", ""),
                        "platform_name": metadata.get("platform_name", ""),
                        "platform_logo_url": metadata.get("platform_logo_url", ""),
                        "associated_tool": metadata.get("associated_tool", ""),
                        "taxonomy": metadata.get("taxonomy", None),
                        "kpi_benefits": metadata.get("kpi_benefits", None),
                        "subscriptions": metadata.get("subscriptions", None)
                    }
                    
                    logger.info(f"Prepared resource data for Weaviate: title={resource_data.get('title')}, platform_name={resource_data.get('platform_name')}, associated_tool={resource_data.get('associated_tool')}, taxonomy={resource_data.get('taxonomy') is not None}, kpi_benefits={resource_data.get('kpi_benefits') is not None}, subscriptions={resource_data.get('subscriptions') is not None}")
                    
                    # Use the specialized add_learning_resource method
                    resource_id = weaviate_client.add_learning_resource(resource_data, tenant_id)
                    logger.info(f"✓ Successfully added learning resource to Weaviate with ID: {resource_id}")
                    logger.info(f"✓ Verified data includes: title={resource_data.get('title')}, type={resource_data.get('resource_type')}, categories={resource_data.get('categories')}")
                elif document_type == "no_code_template" or source_type == "no_code_template":
                    class_name = "NoCodeTemplates"
                    logger.info(f"Storing in NoCodeTemplates class. document_type: {document_type}, source_type: {source_type}")
                    logger.info(f"Template details - Name: {metadata.get('name')}, Platform: {metadata.get('platform')}")
                    # Use the generic add_document method
                    doc_id = weaviate_client.add_document(content, metadata, embedding, class_name=class_name)
                    logger.info(f"Added document chunk {i+1}/{len(processed_chunks)} to Weaviate with ID: {doc_id}")
                elif document_type == "pre_made_prompt" or source_type == "pre_made_prompt":
                    class_name = "Pre_Made_Prompts"
                    logger.info(f"Storing in Pre_Made_Prompts class. document_type: {document_type}, source_type: {source_type}")
                    logger.info(f"Prompt details - Name: {metadata.get('name')}, Associated Tool: {metadata.get('associated_tool')}")
                    # Use the generic add_document method
                    doc_id = weaviate_client.add_document(content, metadata, embedding, class_name=class_name)
                    logger.info(f"Added document chunk {i+1}/{len(processed_chunks)} to Weaviate with ID: {doc_id}")
                elif source_type == "tenant_uploaded_file":
                    class_name = "Tenant_UploadedFiles"
                    
                    # For tenant uploaded files, we need to ensure the content_chunk field is set
                    # Update metadata to include content_chunk
                    metadata["content_chunk"] = content
                    
                    # Ensure required fields are present
                    if "organization_id" not in metadata:
                        logger.error(f"Missing organization_id for tenant uploaded file")
                        continue
                    # Use the generic add_document method
                    doc_id = weaviate_client.add_document(content, metadata, embedding, class_name=class_name)
                    logger.info(f"Added document chunk {i+1}/{len(processed_chunks)} to Weaviate with ID: {doc_id}")
                else:
                    class_name = "Document"
                    # Use the generic add_document method for all other classes
                    doc_id = weaviate_client.add_document(content, metadata, embedding, class_name=class_name)
                    logger.info(f"Added document chunk {i+1}/{len(processed_chunks)} to Weaviate with ID: {doc_id}")
            except Exception as chunk_error:
                logger.error(f"Error storing chunk {i+1}/{len(processed_chunks)} in Weaviate: {str(chunk_error)}")
                # Continue with next chunk instead of failing the entire process
                continue
        
        logger.info(f"Successfully stored {len(processed_chunks)} chunks in Weaviate")
    except Exception as e:
        logger.error(f"Error storing document in Weaviate: {str(e)}")
        raise


def store_in_neo4j_graphrag(
    processed_chunks: List[Dict[str, Any]],
    entities: Dict[str, Any],
    tenant_id: str,
    neo4j_graphrag_client: Neo4jGraphRAGClient
) -> None:
    """
    Store document and build knowledge graph using Neo4j GraphRAG client.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        entities: Dictionary with extracted entities and relationships
        tenant_id: The tenant ID for multi-tenancy
        neo4j_graphrag_client: The Neo4j GraphRAG client
    """
    logger.info(f"Building knowledge graph using Neo4j GraphRAG for tenant {tenant_id}")
    
    # Check if we have valid processed_chunks
    if not processed_chunks:
        logger.warning(f"No processed chunks to build knowledge graph for tenant {tenant_id}")
        return
    
    try:
        from src.core.security import validate_metadata
        
        # Get document metadata from the first chunk
        if processed_chunks:
            document_metadata = processed_chunks[0]["metadata"].copy()
            # Validate and ensure tenant isolation
            document_metadata = validate_metadata(document_metadata, tenant_id)
            document_id = document_metadata.get("document_id", "")
        else:
            document_metadata = {"tenant_id": tenant_id}
            document_id = ""
        
        # Combine all chunks into full text for knowledge graph construction
        full_text = "\n\n".join([chunk["content"] for chunk in processed_chunks])
        
        # Build knowledge graph using the GraphRAG pipeline
        result = neo4j_graphrag_client.build_knowledge_graph(
            text=full_text,
            doc_id=document_id,
            metadata=document_metadata,
            tenant_id=tenant_id
        )
        
        logger.info(f"Successfully built knowledge graph with {len(result.get('entities', []))} entities")
        
    except Exception as e:
        logger.error(f"Error building knowledge graph with Neo4j GraphRAG: {str(e)}")
        raise


def store_in_neo4j(
    processed_chunks: List[Dict[str, Any]],
    entities: Dict[str, Any],
    tenant_id: str,
    neo4j_client: Neo4jClient
) -> None:
    """
    Store document chunks and entities in Neo4j.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        entities: Dictionary with extracted entities and relationships
        tenant_id: The tenant ID for multi-tenancy
        neo4j_client: The Neo4j client
    """
    logger.info(f"Storing document chunks and entities in Neo4j for tenant {tenant_id}")
    
    # Check if we have valid processed_chunks
    if not processed_chunks:
        logger.warning(f"No processed chunks to store in Neo4j for tenant {tenant_id}")
        return
    
    # Check if this is a global tool, no-code template, or other special type
    first_chunk = processed_chunks[0]
    chunk_metadata = first_chunk.get("metadata", {})
    source_type = chunk_metadata.get("source_type", "")
    document_type = chunk_metadata.get("document_type", "")
    
    # Handle global tools
    if source_type == "global_tool" or document_type == "global_tool":
        logger.info("Processing global tool for Neo4j graph creation")
        try:
            # Create Tool node in Neo4j
            tool_id = chunk_metadata.get("tool_id", str(uuid4()))
            
            # Extract categories
            categories = chunk_metadata.get("categories", {})
            primary_category = categories.get("primary", "") if isinstance(categories, dict) else ""
            secondary_categories = categories.get("secondary", []) if isinstance(categories, dict) else []
            
            # Create the tool node
            neo4j_client.query("""
                CREATE (t:Tool {
                    tool_id: $tool_id,
                    name: $name,
                    homepage_url: $homepage_url,
                    last_scraped_at: $last_scraped_at,
                    short_description: $short_description,
                    detailed_description: $detailed_description,
                    rating: $rating,
                    logo_url: $logo_url,
                    tenant_id: $tenant_id
                })
            """, {
                "tool_id": tool_id,
                "name": chunk_metadata.get("name", ""),
                "homepage_url": chunk_metadata.get("homepage_url", ""),
                "last_scraped_at": chunk_metadata.get("last_scraped_at", ""),
                "short_description": chunk_metadata.get("short_description", ""),
                "detailed_description": chunk_metadata.get("detailed_description", ""),
                "rating": float(chunk_metadata.get("rating", 0.0)),
                "logo_url": chunk_metadata.get("logo_url", ""),
                "tenant_id": tenant_id
            })
            logger.info(f"Created Tool node in Neo4j with ID: {tool_id}")
            
            # Create and connect primary Category node
            if primary_category:
                neo4j_client.query("""
                    MERGE (c:Category {name: $primary_category, tenant_id: $tenant_id})
                    WITH c
                    MATCH (t:Tool {tool_id: $tool_id})
                    MERGE (t)-[:HAS_PRIMARY_CATEGORY]->(c)
                """, {"primary_category": primary_category, "tool_id": tool_id, "tenant_id": tenant_id})
                logger.info(f"Connected primary category: {primary_category}")
            
            # Create and connect secondary Category nodes
            for secondary_category in secondary_categories:
                neo4j_client.query("""
                    MERGE (c:Category {name: $secondary_category, tenant_id: $tenant_id})
                    WITH c
                    MATCH (t:Tool {tool_id: $tool_id})
                    MERGE (t)-[:HAS_SECONDARY_CATEGORY]->(c)
                """, {"secondary_category": secondary_category, "tool_id": tool_id, "tenant_id": tenant_id})
                logger.info(f"Connected secondary category: {secondary_category}")
            
            # Create Feature nodes and relationships
            for feature in chunk_metadata.get("features", []):
                if isinstance(feature, dict):
                    feature_name = feature.get("name", "")
                    neo4j_client.query("""
                        MERGE (f:Feature {
                            name: $feature_name,
                            description: $description,
                            use_case: $use_case,
                            tenant_id: $tenant_id
                        })
                        WITH f
                        MATCH (t:Tool {tool_id: $tool_id})
                        MERGE (t)-[:HAS_FEATURE]->(f)
                    """, {
                        "feature_name": feature_name,
                        "description": feature.get("description", ""),
                        "use_case": feature.get("use_case", ""),
                        "tool_id": tool_id,
                        "tenant_id": tenant_id
                    })
                    logger.info(f"Connected feature: {feature_name}")
            
            # Create Tag nodes and relationships
            for tag in chunk_metadata.get("tags", []):
                neo4j_client.query("""
                    MERGE (tag:Tag {name: $tag, tenant_id: $tenant_id})
                    WITH tag
                    MATCH (t:Tool {tool_id: $tool_id})
                    MERGE (t)-[:HAS_TAG]->(tag)
                """, {"tag": tag, "tool_id": tool_id, "tenant_id": tenant_id})
                logger.info(f"Connected tag: {tag}")
            
            logger.info("Successfully built Neo4j knowledge graph for global tool")
            return
        except Exception as e:
            logger.error(f"Error creating Neo4j graph for global tool: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    # Handle global learning resources
    elif source_type == "global_learning_resource" or document_type == "learning_resource":
        logger.info("=== Processing learning resource for Neo4j graph creation ===")
        try:
            # Create LearningResource node in Neo4j
            resource_id = chunk_metadata.get("resource_id", str(uuid4()))
            
            # Extract categories
            categories = chunk_metadata.get("categories", {})
            primary_category = categories.get("primary", "") if isinstance(categories, dict) else ""
            secondary_categories = categories.get("secondary", []) if isinstance(categories, dict) else []
            
            # Extract target audience
            target_audience = chunk_metadata.get("target_audience", {})
            expertise_level = target_audience.get("expertise_level", "") if isinstance(target_audience, dict) else ""
            job_roles = target_audience.get("job_roles", []) if isinstance(target_audience, dict) else []
            
            # Create the learning resource node
            logger.info(f"Creating LearningResource node with ID: {resource_id}")
            neo4j_client.query("""
                CREATE (lr:LearningResource {
                    resource_id: $resource_id,
                    title: $title,
                    description: $description,
                    source_url: $source_url,
                    resource_type: $resource_type,
                    expertise_level: $expertise_level,
                    estimated_time: $estimated_time,
                    tenant_id: $tenant_id
                })
            """, {
                "resource_id": resource_id,
                "title": chunk_metadata.get("title", ""),
                "description": chunk_metadata.get("description", ""),
                "source_url": chunk_metadata.get("source_url", ""),
                "resource_type": chunk_metadata.get("resource_type", ""),
                "expertise_level": expertise_level,
                "estimated_time": chunk_metadata.get("estimatedTime", ""),
                "tenant_id": tenant_id
            })
            logger.info(f"✓ Created LearningResource node in Neo4j with ID: {resource_id}")
            
            # Create and connect primary Category node
            if primary_category:
                logger.info(f"Creating primary category relationship: {primary_category}")
                neo4j_client.query("""
                    MERGE (c:Category {name: $primary_category, tenant_id: $tenant_id})
                    WITH c
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:HAS_PRIMARY_CATEGORY]->(c)
                """, {"primary_category": primary_category, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected primary category: {primary_category}")
            
            # Create and connect secondary Category nodes
            for secondary_category in secondary_categories:
                logger.info(f"Creating secondary category relationship: {secondary_category}")
                neo4j_client.query("""
                    MERGE (c:Category {name: $secondary_category, tenant_id: $tenant_id})
                    WITH c
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:HAS_SECONDARY_CATEGORY]->(c)
                """, {"secondary_category": secondary_category, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected secondary category: {secondary_category}")
            
            # Create Topic nodes and relationships
            for topic in chunk_metadata.get("topics_discussed", []):
                logger.info(f"Creating topic relationship: {topic}")
                neo4j_client.query("""
                    MERGE (t:Topic {name: $topic, tenant_id: $tenant_id})
                    WITH t
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:DISCUSSES_TOPIC]->(t)
                """, {"topic": topic, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected topic: {topic}")
            
            # Create JobRole nodes and relationships
            for job_role in job_roles:
                logger.info(f"Creating job role relationship: {job_role}")
                neo4j_client.query("""
                    MERGE (jr:JobRole {name: $job_role, tenant_id: $tenant_id})
                    WITH jr
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:TARGETS_JOB_ROLE]->(jr)
                """, {"job_role": job_role, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected job role: {job_role}")
            
            # Create UseContext nodes and relationships
            for context in chunk_metadata.get("useful_context", []):
                logger.info(f"Creating use context relationship: {context}")
                neo4j_client.query("""
                    MERGE (uc:UseContext {name: $context, tenant_id: $tenant_id})
                    WITH uc
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:USEFUL_IN_CONTEXT]->(uc)
                """, {"context": context, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected use context: {context}")
            
            # Create Tag nodes and relationships
            for tag in chunk_metadata.get("tags", []):
                logger.info(f"Creating tag relationship: {tag}")
                neo4j_client.query("""
                    MERGE (tag:Tag {name: $tag, tenant_id: $tenant_id})
                    WITH tag
                    MATCH (lr:LearningResource {resource_id: $resource_id})
                    MERGE (lr)-[:HAS_TAG]->(tag)
                """, {"tag": tag, "resource_id": resource_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected tag: {tag}")
            
            logger.info("✓ Successfully built Neo4j knowledge graph for learning resource")
            return
        except Exception as e:
            logger.error(f"Error creating Neo4j graph for learning resource: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    # Handle no-code templates
    elif source_type == "no_code_template" or document_type == "no_code_template":
        logger.info("Processing no-code template for Neo4j graph creation")
        try:
            # Create Template node
            template_id = chunk_metadata.get("template_id", str(uuid4()))
            
            neo4j_client.query("""
                CREATE (t:Template {
                    name: $name,
                    uuid: $uuid,
                    source_url: $source_url,
                    platform: $platform,
                    short_description: $short_description,
                    complexity: $complexity,
                    tenant_id: $tenant_id
                })
            """, {
                "name": chunk_metadata.get("name", ""),
                "uuid": template_id,
                "source_url": chunk_metadata.get("source_url", ""),
                "platform": chunk_metadata.get("platform", ""),
                "short_description": chunk_metadata.get("short_description", ""),
                "complexity": chunk_metadata.get("complexity", ""),
                "tenant_id": tenant_id
            })
            logger.info(f"Created Template node in Neo4j with ID: {template_id}")
            
            # Create and connect UseCase nodes
            for use_case in chunk_metadata.get("use_cases", []):
                neo4j_client.query("""
                    MERGE (uc:UseCase {name: $use_case, tenant_id: $tenant_id})
                    WITH uc
                    MATCH (t:Template {uuid: $uuid})
                    MERGE (t)-[:HAS_USE_CASE]->(uc)
                """, {"use_case": use_case, "uuid": template_id, "tenant_id": tenant_id})
                logger.info(f"Connected use case: {use_case}")
            
            # Create and connect primary Category node
            categories = chunk_metadata.get("categories", {})
            if isinstance(categories, dict):
                primary_category = categories.get("primary")
                if primary_category:
                    neo4j_client.query("""
                        MERGE (c:Category {name: $primary_category, tenant_id: $tenant_id})
                        WITH c
                        MATCH (t:Template {uuid: $uuid})
                        MERGE (t)-[:HAS_PRIMARY_CATEGORY]->(c)
                    """, {"primary_category": primary_category, "uuid": template_id, "tenant_id": tenant_id})
                    logger.info(f"Connected primary category: {primary_category}")
                
                # Create and connect secondary Category nodes
                for secondary_category in categories.get("secondary", []):
                    neo4j_client.query("""
                        MERGE (c:Category {name: $secondary_category, tenant_id: $tenant_id})
                        WITH c
                        MATCH (t:Template {uuid: $uuid})
                        MERGE (t)-[:HAS_SECONDARY_CATEGORY]->(c)
                    """, {"secondary_category": secondary_category, "uuid": template_id, "tenant_id": tenant_id})
                    logger.info(f"Connected secondary category: {secondary_category}")
            
            # Create Platform node and relationship
            platform = chunk_metadata.get("platform")
            if platform:
                neo4j_client.query("""
                    MERGE (p:Platform {name: $platform, tenant_id: $tenant_id})
                    WITH p
                    MATCH (t:Template {uuid: $uuid})
                    MERGE (t)-[:RUNS_ON]->(p)
                """, {"platform": platform, "uuid": template_id, "tenant_id": tenant_id})
                logger.info(f"Connected platform: {platform}")
            
            logger.info("Successfully built Neo4j knowledge graph for no-code template")
            return
        except Exception as e:
            logger.error(f"Error creating Neo4j graph for no-code template: {str(e)}")
            raise
    
    # Handle global ecosystem partners
    elif source_type == "global_ecosystem_partner" or document_type == "ecosystem_partner":
        logger.info("Processing ecosystem partner for Neo4j graph creation")
        try:
            # Create EcosystemPartner node in Neo4j
            partner_id = chunk_metadata.get("partner_id", str(uuid4()))
            
            # Create the ecosystem partner node
            logger.info(f"Creating EcosystemPartner node with ID: {partner_id}")
            neo4j_client.query("""
                CREATE (ep:EcosystemPartner {
                    partner_id: $partner_id,
                    name: $name,
                    bio: $bio,
                    website: $website,
                    contact_info: $contact_info,
                    budget_tier: $budget_tier,
                    case_studies: $case_studies,
                    tenant_id: $tenant_id
                })
            """, {
                "partner_id": partner_id,
                "name": chunk_metadata.get("name", ""),
                "bio": chunk_metadata.get("bio", ""),
                "website": chunk_metadata.get("website", ""),
                "contact_info": chunk_metadata.get("contact_info", ""),
                "budget_tier": chunk_metadata.get("budget_tier", ""),
                "case_studies": chunk_metadata.get("case_studies", ""),
                "tenant_id": tenant_id
            })
            logger.info(f"✓ Created EcosystemPartner node in Neo4j with ID: {partner_id}")
            
            # Create Expertise nodes and relationships
            for expertise in chunk_metadata.get("expertise", []):
                logger.info(f"Creating expertise relationship: {expertise}")
                neo4j_client.query("""
                    MERGE (e:Expertise {name: $expertise, tenant_id: $tenant_id})
                    WITH e
                    MATCH (ep:EcosystemPartner {partner_id: $partner_id})
                    MERGE (ep)-[:HAS_EXPERTISE]->(e)
                """, {"expertise": expertise, "partner_id": partner_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected expertise: {expertise}")
            
            # Create Certification nodes and relationships
            for certification in chunk_metadata.get("certifications", []):
                logger.info(f"Creating certification relationship: {certification}")
                neo4j_client.query("""
                    MERGE (c:Certification {name: $certification, tenant_id: $tenant_id})
                    WITH c
                    MATCH (ep:EcosystemPartner {partner_id: $partner_id})
                    MERGE (ep)-[:HAS_CERTIFICATION]->(c)
                """, {"certification": certification, "partner_id": partner_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected certification: {certification}")
            
            # Create Tag nodes and relationships
            for tag in chunk_metadata.get("tags", []):
                logger.info(f"Creating tag relationship: {tag}")
                neo4j_client.query("""
                    MERGE (t:Tag {name: $tag, tenant_id: $tenant_id})
                    WITH t
                    MATCH (ep:EcosystemPartner {partner_id: $partner_id})
                    MERGE (ep)-[:HAS_TAG]->(t)
                """, {"tag": tag, "partner_id": partner_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected tag: {tag}")
            
            # Create BudgetTier node and relationship
            budget_tier = chunk_metadata.get("budget_tier")
            if budget_tier:
                logger.info(f"Creating budget tier relationship: {budget_tier}")
                neo4j_client.query("""
                    MERGE (bt:BudgetTier {name: $budget_tier, tenant_id: $tenant_id})
                    WITH bt
                    MATCH (ep:EcosystemPartner {partner_id: $partner_id})
                    MERGE (ep)-[:OFFERS_TIER]->(bt)
                """, {"budget_tier": budget_tier, "partner_id": partner_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected budget tier: {budget_tier}")
            
            logger.info("✓ Successfully built Neo4j knowledge graph for ecosystem partner")
            return
        except Exception as e:
            logger.error(f"Error creating Neo4j graph for ecosystem partner: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    # Handle pre-made prompts
    elif source_type == "pre_made_prompt" or document_type == "pre_made_prompt":
        logger.info("Processing pre-made prompt for Neo4j graph creation")
        try:
            # Create PreMadePrompt node in Neo4j
            prompt_id = chunk_metadata.get("prompt_id", str(uuid4()))
            
            # Create the pre-made prompt node
            logger.info(f"Creating PreMadePrompt node with ID: {prompt_id}")
            neo4j_client.query("""
                CREATE (pm:PreMadePrompt {
                    prompt_id: $prompt_id,
                    name: $name,
                    prompt_body: $prompt_body,
                    associated_tool: $associated_tool,
                    prompting_technique: $prompting_technique,
                    tenant_id: $tenant_id
                })
            """, {
                "prompt_id": prompt_id,
                "name": chunk_metadata.get("name", ""),
                "prompt_body": chunk_metadata.get("prompt_body", ""),
                "associated_tool": chunk_metadata.get("associated_tool", ""),
                "prompting_technique": chunk_metadata.get("prompting_technique", ""),
                "tenant_id": tenant_id
            })
            logger.info(f"✓ Created PreMadePrompt node in Neo4j with ID: {prompt_id}")
            
            # Create Placeholder nodes and relationships
            for placeholder in chunk_metadata.get("placeholders", []):
                logger.info(f"Creating placeholder relationship: {placeholder}")
                neo4j_client.query("""
                    MERGE (p:Placeholder {name: $placeholder, tenant_id: $tenant_id})
                    WITH p
                    MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                    MERGE (pm)-[:HAS_PLACEHOLDER]->(p)
                """, {"placeholder": placeholder, "prompt_id": prompt_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected placeholder: {placeholder}")
            
            # Create ConcreteTask nodes and relationships
            for task in chunk_metadata.get("concrete_tasks", []):
                logger.info(f"Creating concrete task relationship: {task}")
                neo4j_client.query("""
                    MERGE (ct:ConcreteTask {name: $task, tenant_id: $tenant_id})
                    WITH ct
                    MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                    MERGE (pm)-[:USED_FOR_TASK]->(ct)
                """, {"task": task, "prompt_id": prompt_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected concrete task: {task}")
            
            # Create Taxonomy relationships
            taxonomy = chunk_metadata.get("taxonomy", {})
            if isinstance(taxonomy, dict):
                # Create primary category
                primary_category = taxonomy.get("primary_category")
                if primary_category:
                    neo4j_client.query("""
                        MERGE (c:Category {name: $primary_category, tenant_id: $tenant_id})
                        WITH c
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:HAS_PRIMARY_CATEGORY]->(c)
                    """, {"primary_category": primary_category, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected primary category: {primary_category}")
                
                # Create secondary categories
                for secondary_category in taxonomy.get("secondary_categories", []):
                    neo4j_client.query("""
                        MERGE (c:Category {name: $secondary_category, tenant_id: $tenant_id})
                        WITH c
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:HAS_SECONDARY_CATEGORY]->(c)
                    """, {"secondary_category": secondary_category, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected secondary category: {secondary_category}")
                
                # Create department relationship
                department = taxonomy.get("department")
                if department:
                    neo4j_client.query("""
                        MERGE (d:Department {name: $department, tenant_id: $tenant_id})
                        WITH d
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:BELONGS_TO_DEPARTMENT]->(d)
                    """, {"department": department, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected department: {department}")
                
                # Create team relationship
                team = taxonomy.get("team")
                if team:
                    neo4j_client.query("""
                        MERGE (t:Team {name: $team, tenant_id: $tenant_id})
                        WITH t
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:BELONGS_TO_TEAM]->(t)
                    """, {"team": team, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected team: {team}")
            
            # Create TargetAudience relationship
            target_audience = chunk_metadata.get("target_audience", {})
            if isinstance(target_audience, dict):
                expertise_level = target_audience.get("expertise_level")
                if expertise_level:
                    neo4j_client.query("""
                        MERGE (el:ExpertiseLevel {level: $expertise_level, tenant_id: $tenant_id})
                        WITH el
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:TARGETS_EXPERTISE_LEVEL]->(el)
                    """, {"expertise_level": expertise_level, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected expertise level: {expertise_level}")
                
                # Create JobRole relationships
                for job_role in target_audience.get("job_roles", []):
                    neo4j_client.query("""
                        MERGE (jr:JobRole {name: $job_role, tenant_id: $tenant_id})
                        WITH jr
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:TARGETS_JOB_ROLE]->(jr)
                    """, {"job_role": job_role, "prompt_id": prompt_id, "tenant_id": tenant_id})
                    logger.info(f"✓ Connected job role: {job_role}")
            
            # Create ModelCompatibility nodes and relationships
            for model in chunk_metadata.get("model_compatibility", []):
                logger.info(f"Creating model compatibility relationship: {model}")
                neo4j_client.query("""
                    MERGE (m:AIModel {name: $model, tenant_id: $tenant_id})
                    WITH m
                    MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                    MERGE (pm)-[:COMPATIBLE_WITH]->(m)
                """, {"model": model, "prompt_id": prompt_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected AI model: {model}")
            
            # Create Tag nodes and relationships
            for tag in chunk_metadata.get("tags", []):
                logger.info(f"Creating tag relationship: {tag}")
                neo4j_client.query("""
                    MERGE (t:Tag {name: $tag, tenant_id: $tenant_id})
                    WITH t
                    MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                    MERGE (pm)-[:HAS_TAG]->(t)
                """, {"tag": tag, "prompt_id": prompt_id, "tenant_id": tenant_id})
                logger.info(f"✓ Connected tag: {tag}")
            
            # Create KPI Benefits relationship
            kpi_benefits = chunk_metadata.get("kpi_benefits", {})
            if isinstance(kpi_benefits, dict):
                kpi_name = kpi_benefits.get("kpi_name")
                if kpi_name:
                    neo4j_client.query("""
                        CREATE (kpi:KPIBenefit {
                            name: $kpi_name,
                            expected_improvement: $expected_improvement,
                            measurement_method: $measurement_method,
                            baseline_value: $baseline_value,
                            target_value: $target_value,
                            tenant_id: $tenant_id
                        })
                        WITH kpi
                        MATCH (pm:PreMadePrompt {prompt_id: $prompt_id})
                        MERGE (pm)-[:IMPROVES_KPI]->(kpi)
                    """, {
                        "kpi_name": kpi_name,
                        "expected_improvement": kpi_benefits.get("expected_improvement", ""),
                        "measurement_method": kpi_benefits.get("measurement_method", ""),
                        "baseline_value": kpi_benefits.get("baseline_value", ""),
                        "target_value": kpi_benefits.get("target_value", ""),
                        "prompt_id": prompt_id,
                        "tenant_id": tenant_id
                    })
                    logger.info(f"✓ Connected KPI benefit: {kpi_name}")
            
            logger.info("✓ Successfully built Neo4j knowledge graph for pre-made prompt")
            return
        except Exception as e:
            logger.error(f"Error creating Neo4j graph for pre-made prompt: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    # For other document types, check if we have entities
    if not entities or not entities.get("entities"):
        logger.warning(f"No entities to store in Neo4j for tenant {tenant_id}")
        return
    
    try:
        from src.core.security import validate_metadata
        
        # Extract entities and relationships
        entity_list = entities.get("entities", [])
        relationship_list = entities.get("relationships", [])
        
        logger.info(f"Storing {len(entity_list)} entities and {len(relationship_list)} relationships in Neo4j")
        
        # Get document metadata from the first chunk
        if processed_chunks:
            document_metadata = processed_chunks[0]["metadata"].copy()
            # Validate and ensure tenant isolation
            document_metadata = validate_metadata(document_metadata, tenant_id)
            document_id = document_metadata.get("document_id", "")
        else:
            document_metadata = {"tenant_id": tenant_id}
            document_id = ""
        
        # Store entities in Neo4j
        for entity in entity_list:
            try:
                # Ensure tenant isolation
                entity["tenant_id"] = tenant_id
                
                # Add the entity to Neo4j
                neo4j_client.add_entity(
                    entity_id=entity.get("id", ""),
                    name=entity.get("name", ""),
                    entity_type=entity.get("type", ""),
                    properties={
                        **document_metadata,
                        "document_id": document_id,
                        "chunk_id": entity.get("chunk_id", ""),
                        "tenant_id": tenant_id
                    }
                )
            except Exception as entity_error:
                logger.error(f"Error storing entity in Neo4j: {str(entity_error)}")
                # Continue with next entity instead of failing the entire process
                continue
        
        # Store relationships in Neo4j
        for relationship in relationship_list:
            try:
                # Ensure tenant isolation
                relationship["tenant_id"] = tenant_id
                
                # Add the relationship to Neo4j
                try:
                    # Prepare relationship properties
                    rel_properties = {
                        "document_id": document_id,
                        "description": relationship.get("description", ""),
                        "chunk_id": relationship.get("chunk_id", ""),
                        "tenant_id": tenant_id
                    }
                    
                    # Add document metadata, but ensure nested dictionaries are handled properly
                    for key, value in document_metadata.items():
                        # Skip adding nested dictionaries directly
                        if not isinstance(value, dict):
                            rel_properties[key] = value
                    
                    neo4j_client.add_relationship(
                        source_id=relationship.get("source_id", ""),
                        target_id=relationship.get("target_id", ""),
                        rel_type=relationship.get("type", ""),
                        properties=rel_properties
                    )
                except Exception as rel_error:
                    logger.error(f"Error storing relationship in Neo4j: {str(rel_error)}")
                    # Continue with next relationship instead of failing the entire process
                    continue
            except Exception as rel_error:
                logger.error(f"Error storing relationship in Neo4j: {str(rel_error)}")
                # Continue with next relationship instead of failing the entire process
                continue
        
        logger.info(f"Successfully stored entities and relationships in Neo4j")
    except Exception as e:
        logger.error(f"Error storing document in Neo4j: {str(e)}")
        raise


async def store_in_weaviate_async(
    processed_chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    tenant_id: str,
    weaviate_client: WeaviateClient
) -> None:
    """
    Store document chunks and embeddings in Weaviate asynchronously.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        embeddings: List of embeddings for each chunk
        tenant_id: The tenant ID for multi-tenancy
        weaviate_client: The Weaviate client
    """
    logger.info(f"Storing document chunks in Weaviate asynchronously for tenant {tenant_id}")
    
    try:
        # Run synchronous Weaviate operations in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            store_in_weaviate,
            processed_chunks,
            embeddings,
            tenant_id,
            weaviate_client
        )
        
        logger.info(f"Successfully stored chunks in Weaviate asynchronously")
    except Exception as e:
        logger.error(f"Error storing document in Weaviate asynchronously: {str(e)}")
        raise


async def store_in_neo4j_async(
    processed_chunks: List[Dict[str, Any]],
    entities: Dict[str, Any],
    tenant_id: str,
    neo4j_client: Neo4jClient
) -> None:
    """
    Store document chunks and entities in Neo4j asynchronously.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        entities: Dictionary with extracted entities and relationships
        tenant_id: The tenant ID for multi-tenancy
        neo4j_client: The Neo4j client
    """
    logger.info(f"Storing document chunks and entities in Neo4j asynchronously for tenant {tenant_id}")
    
    try:
        # Run synchronous Neo4j operations in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            store_in_neo4j,
            processed_chunks,
            entities,
            tenant_id,
            neo4j_client
        )
        
        logger.info(f"Successfully stored entities and relationships in Neo4j asynchronously")
    except Exception as e:
        logger.error(f"Error storing document in Neo4j asynchronously: {str(e)}")
        raise


async def store_in_neo4j_graphrag_async(
    processed_chunks: List[Dict[str, Any]],
    entities: Dict[str, Any],
    tenant_id: str,
    neo4j_graphrag_client: Neo4jGraphRAGClient
) -> None:
    """
    Store document and build knowledge graph using Neo4j GraphRAG client asynchronously.
    
    Args:
        processed_chunks: List of document chunks with content and metadata
        entities: Dictionary with extracted entities and relationships
        tenant_id: The tenant ID for multi-tenancy
        neo4j_graphrag_client: The Neo4j GraphRAG client
    """
    logger.info(f"Building knowledge graph using Neo4j GraphRAG asynchronously for tenant {tenant_id}")
    
    try:
        # Run synchronous GraphRAG operations in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            store_in_neo4j_graphrag,
            processed_chunks,
            entities,
            tenant_id,
            neo4j_graphrag_client
        )
        
        logger.info(f"Successfully built knowledge graph asynchronously")
    except Exception as e:
        logger.error(f"Error building knowledge graph asynchronously: {str(e)}")
        raise


def fetch_and_extract_text(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch a file from Google Cloud Storage and extract its raw text content.
    
    Args:
        state: The current state containing file_id, organization_id, gcs_path, etc.
        
    Returns:
        Updated state with raw_text field populated
    """
    logger.info(f"Fetching and extracting text from GCS path: {state.get('gcs_path')}")
    
    try:
        # Initialize state if not present
        if 'status' not in state:
            state['status'] = 'pending'
        if 'processing_log' not in state:
            state['processing_log'] = []
        
        # Update status
        state['status'] = 'processing'
        state['processing_log'].append(f"Started fetching file from {state.get('gcs_path')} at {datetime.now(timezone.utc).isoformat()}")
        
        # Get the GCS path
        gcs_path = state.get('gcs_path')
        if not gcs_path:
            error_msg = "No GCS path provided in state"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
        
        # Parse the GCS path to get bucket and blob name
        # Format: gs://bucket-name/path/to/file
        if gcs_path.startswith('gs://'):
            gcs_path = gcs_path[5:]  # Remove 'gs://'
        
        # Split into bucket and blob path
        parts = gcs_path.split('/', 1)
        if len(parts) < 2:
            error_msg = f"Invalid GCS path format: {gcs_path}"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        bucket_name = parts[0]
        blob_name = parts[1]
        
        # Determine file extension from blob name
        file_extension = Path(blob_name).suffix.lower()
        
        # Create a temporary file to store the downloaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
            try:
                # Mock GCS functionality since the library is not available
                # In a real implementation, we would use the Google Cloud Storage client
                # to download the file from GCS
                
                # Create a mock file with some sample content based on the file extension
                with open(temp_path, 'w') as f:
                    if file_extension == '.pdf':
                        f.write("This is a mock PDF content for testing.\nPage 1\nThis is a sample document.\n")
                        f.write(f"Document ID: {state.get('file_id')}\n")
                        f.write(f"Organization: {state.get('organization_id')}\n")
                        f.write("This is the end of the mock PDF content.")
                    elif file_extension in ['.txt', '.md']:
                        f.write("This is a mock text file content for testing.\n")
                        f.write(f"Document ID: {state.get('file_id')}\n")
                        f.write(f"Organization: {state.get('organization_id')}\n")
                    else:
                        f.write(f"Mock content for {file_extension} file type.\n")
                        f.write(f"Document ID: {state.get('file_id')}\n")
                        f.write(f"Organization: {state.get('organization_id')}\n")
                
                state['processing_log'].append(f"Created mock file at temporary location: {temp_path}")
                
                # Determine file type from blob name
                file_extension = Path(blob_name).suffix.lower()
                
                # Extract text based on file type
                if file_extension == '.pdf':
                    # Use PyMuPDF for PDF extraction
                    loader = PyMuPDFLoader(temp_path)
                    documents = loader.load()
                    raw_text = "\n\n".join([doc.page_content for doc in documents])
                elif file_extension in ['.txt', '.md', '.csv', '.json']:
                    # Use appropriate loader based on file type
                    if file_extension == '.csv':
                        loader = CSVLoader(temp_path)
                    else:
                        loader = TextLoader(temp_path)
                    documents = loader.load()
                    raw_text = "\n\n".join([doc.page_content for doc in documents])
                else:
                    # Use a generic loader for other file types
                    loader = UnstructuredFileLoader(temp_path)
                    documents = loader.load()
                    raw_text = "\n\n".join([doc.page_content for doc in documents])
                
                # Update state with extracted text
                state['raw_text'] = raw_text
                state['processing_log'].append(f"Successfully extracted {len(raw_text)} characters of text")
                
            except Exception as e:
                error_msg = f"Error processing file from GCS: {str(e)}"
                logger.error(error_msg)
                state['processing_log'].append(f"Error: {error_msg}")
                state['status'] = 'failed'
                return state
        
        
        # Update status to indicate successful processing
        state['status'] = 'text_extracted'
        state['processing_log'].append(f"Completed text extraction at {datetime.now(timezone.utc).isoformat()}")
        
        return state
    except Exception as e:
        logger.error(f"Unexpected error in fetch_and_extract_text: {str(e)}")
        if 'processing_log' in state:
            state['processing_log'].append(f"Critical error: {str(e)}")
        state['status'] = 'failed'
        return state
        
        # Update status to indicate successful processing
        state['status'] = 'text_extracted'
        state['processing_log'].append(f"Completed text extraction at {datetime.now(timezone.utc).isoformat()}")
        
        return state

    
def generate_embeddings(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate embeddings for each text chunk in the state.
    
    Args:
        state: The current state containing chunks and other fields
        
    Returns:
        Updated state with vectors added to each chunk
    """
    logger.info("Generating embeddings for text chunks")
    
    try:
        # Initialize state if not present
        if 'status' not in state:
            state['status'] = 'processing'
        if 'processing_log' not in state:
            state['processing_log'] = []
        if 'chunks' not in state:
            state['chunks'] = []
            
        # Update status
        state['processing_log'].append(f"Started embedding generation at {datetime.now(timezone.utc).isoformat()}")
        
        # Get the chunks
        chunks = state.get('chunks', [])
        if not chunks:
            error_msg = "No chunks available for embedding generation"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Initialize OpenAI embeddings
        api_key = settings.OPENAI_API_KEY
        
        embeddings_model = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=settings.EMBEDDING_MODEL,
            openai_organization=settings.OPENAI_ORGANIZATION if hasattr(settings, 'OPENAI_ORGANIZATION') else None
        )
        
        # Extract texts from chunks
        texts = [chunk.get("content", "") for chunk in chunks]
        
        # Generate embeddings for all chunks
        vectors = embeddings_model.embed_documents(texts)
        
        # Add vectors to chunks
        for i, chunk in enumerate(chunks):
            chunk["vector"] = vectors[i]
        
        # Update state
        state['chunks'] = chunks
        state['status'] = 'embedded'
        state['processing_log'].append(f"Generated embeddings for {len(chunks)} chunks")
        state['processing_log'].append(f"Completed embedding generation at {datetime.now(timezone.utc).isoformat()}")
        
        return state
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_embeddings: {str(e)}")
        if 'processing_log' in state:
            state['processing_log'].append(f"Critical error in embedding generation: {str(e)}")
        state['status'] = 'failed'
        return state
def persist_to_weaviate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Batch-insert embedded chunks into the tenant-specific Weaviate class (Tenant_UploadedFiles).
    
    Args:
        state: The current state containing chunks with embeddings and other fields
        
    Returns:
        Updated state with status set to 'weaviate_persisted'
    """
    logger.info("Persisting embedded chunks to Weaviate")
    
    try:
        # Initialize state if not present
        if 'status' not in state:
            state['status'] = 'processing'
        if 'processing_log' not in state:
            state['processing_log'] = []
            
        # Update status
        state['processing_log'].append(f"Started persisting to Weaviate at {datetime.now(timezone.utc).isoformat()}")
        
        # Get the chunks with embeddings
        chunks = state.get('chunks', [])
        if not chunks:
            error_msg = "No chunks available for persisting to Weaviate"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Get organization_id from state
        organization_id = state.get('organization_id')
        if not organization_id:
            error_msg = "No organization_id available in state"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Get file_id from state
        file_id = state.get('file_id')
        if not file_id:
            error_msg = "No file_id available in state"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Get tenant_id from state, default to "default"
        tenant_id = state.get('tenant_id', "default")
        
        # Initialize Weaviate client
        weaviate_client = WeaviateClient(
            weaviate_url=settings.WEAVIATE_URL,
            api_key=settings.WEAVIATE_API_KEY
        )
        
        # Batch insert chunks with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        successful_inserts = 0
        failed_inserts = 0
        
        for chunk in chunks:
            # Extract content and vector from chunk
            content = chunk.get("content", "")
            vector = chunk.get("vector", [])
            
            if not content or not vector:
                logger.warning(f"Skipping chunk without content or vector")
                failed_inserts += 1
                continue
                
            # Prepare metadata for Weaviate
            metadata = {
                "file_id": file_id,
                "organization_id": organization_id,
                "file_name": state.get("file_name", ""),
                "file_path": state.get("gcs_path", ""),
                "content_chunk": content,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "file_type": state.get("file_type", ""),
                "tags": state.get("tags", []),
                "tenant_id": tenant_id,
                "chunk_id": chunk.get("metadata", {}).get("chunk_id", "")
            }
            
            # Apply retry logic for each chunk
            for attempt in range(max_retries):
                try:
                    # Add to Weaviate
                    weaviate_client.add_tenant_uploaded_file(
                        file_data=metadata,
                        organization_id=organization_id,
                        tenant_id=tenant_id
                    )
                    successful_inserts += 1
                    break  # Break the retry loop if successful
                except Exception as e:
                    logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        # Wait before retrying with exponential backoff
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Failed to insert chunk after {max_retries} attempts: {str(e)}")
                        failed_inserts += 1
        
        # Update status
        if failed_inserts > 0:
            if successful_inserts > 0:
                state['status'] = 'partially_persisted'
                state['processing_log'].append(f"Partially persisted to Weaviate: {successful_inserts} successful, {failed_inserts} failed")
            else:
                state['status'] = 'failed'
                state['processing_log'].append(f"Failed to persist any chunks to Weaviate")
        else:
            state['status'] = 'weaviate_persisted'
            state['processing_log'].append(f"Successfully persisted {successful_inserts} chunks to Weaviate")
        
        state['processing_log'].append(f"Completed persisting to Weaviate at {datetime.now(timezone.utc).isoformat()}")
        
        return state
    
    except Exception as e:
        logger.error(f"Unexpected error in persist_to_weaviate: {str(e)}")
        if 'processing_log' in state:
            state['processing_log'].append(f"Critical error in persisting to Weaviate: {str(e)}")
        state['status'] = 'failed'
        return state

def persist_to_neo4j(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate extracted entities and relations into Cypher queries to create nodes and edges in Neo4j.
    
    Args:
        state: The current state containing entities_and_relations and other fields
        
    Returns:
        Updated state with status set to 'neo4j_persisted'
    """
    logger.info("Translating entities and relations into Cypher queries for Neo4j persistence")
    
    try:
        # Initialize state if not present
        if 'status' not in state:
            state['status'] = 'processing'
        if 'processing_log' not in state:
            state['processing_log'] = []
            
        # Update status
        state['processing_log'].append(f"Started persisting to Neo4j at {datetime.now(timezone.utc).isoformat()}")
        
        # Get the entities and relations
        entities_and_relations = state.get('entities_and_relations', {})
        
        # Check if entities_and_relations is None or empty dict
        if not entities_and_relations or (isinstance(entities_and_relations, dict) and not any(entities_and_relations.values())):
            logger.warning("Empty content provided for entity extraction")
            state['processing_log'].append("Warning: No entities and relations available for persisting to Neo4j")
            # Don't fail, just log the warning and continue with document creation
            
        # Get file_id and organization_id from state
        file_id = state.get('file_id')
        if not file_id:
            error_msg = "No file_id available in state"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        organization_id = state.get('organization_id')
        if not organization_id:
            error_msg = "No organization_id available in state"
            logger.error(error_msg)
            state['processing_log'].append(f"Error: {error_msg}")
            state['status'] = 'failed'
            return state
            
        # Get tenant_id from state, default to "default"
        tenant_id = state.get('tenant_id', "default")
        
        # Initialize Neo4j client
        neo4j_client = Neo4jClient(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        
        # Extract entities and relationships
        entities = entities_and_relations.get("entities", []) if entities_and_relations else []
        relationships = entities_and_relations.get("relationships", []) if entities_and_relations else []
        
        # Log warning if no entities found
        if not entities and not relationships:
            logger.warning(f"No entities or relationships extracted for document {file_id}")
            state['processing_log'].append(f"Warning: No entities or relationships extracted for document {file_id}")
        else:
            logger.info(f"Persisting {len(entities)} entities and {len(relationships)} relationships to Neo4j")
        
        # Create a document node for the file
        document_metadata = {
            "file_id": file_id,
            "organization_id": organization_id,
            "tenant_id": tenant_id,
            "gcs_path": state.get("gcs_path", ""),
            "file_name": state.get("file_name", ""),
            "file_type": state.get("file_type", ""),
            "upload_date": datetime.now(timezone.utc).isoformat()
        }
        
        # Create document node in Neo4j
        document_id = file_id
        neo4j_client.add_document(
            document_id=document_id,
            content=state.get("raw_text", ""),
            metadata=document_metadata
        )
        
        state['processing_log'].append(f"Created document node in Neo4j with ID: {document_id}")
        
        # Create entity nodes and relationships to the document
        for entity in entities:
            try:
                # Generate a unique ID for the entity if not present
                entity_id = entity.get("id", str(uuid4()))
                
                # Add entity to Neo4j
                neo4j_client.add_entity(
                    entity_id=entity_id,
                    name=entity.get("name", ""),
                    entity_type=entity.get("type", ""),
                    properties={
                        "document_id": document_id,
                        "tenant_id": tenant_id,
                        "organization_id": organization_id
                    }
                )
                
                # Create relationship between document and entity
                with neo4j_client.driver.session() as session:
                    session.run("""
                        MATCH (d:Document {id: $doc_id})
                        MATCH (e:Entity {id: $entity_id})
                        MERGE (d)-[:MENTIONS]->(e)
                    """, {
                        "doc_id": document_id,
                        "entity_id": entity_id
                    })
                
                state['processing_log'].append(f"Created entity node in Neo4j: {entity.get('name')}")
            except Exception as e:
                logger.error(f"Error creating entity {entity.get('name')}: {str(e)}")
                state['processing_log'].append(f"Error creating entity {entity.get('name')}: {str(e)}")
                continue
        
        # Create relationships between entities
        for relationship in relationships:
            try:
                # Check if relationship has source_id and target_id
                source_id = relationship.get("source_id")
                target_id = relationship.get("target_id")
                source_name = relationship.get("source")
                target_name = relationship.get("target")
                rel_type = relationship.get("type", "RELATED_TO").replace(" ", "_").replace("-", "_").upper()
                
                # If source_id and target_id are not provided, try to find them by name
                if not source_id or not target_id:
                    # Find source and target entity IDs
                    source_id = None
                    target_id = None
                    
                    # Find entities by name to get their IDs
                    for e in entities:
                        if e.get("name") == source_name:
                            source_id = e.get("id")
                        if e.get("name") == target_name:
                            target_id = e.get("id")
                
                # If we found both entity IDs, use add_relationship method
                if source_id and target_id:
                    # Prepare relationship properties
                    rel_properties = {
                        "document_id": document_id,
                        "tenant_id": tenant_id,
                        "organization_id": organization_id,
                        "description": relationship.get("description", "")
                    }
                    
                    neo4j_client.add_relationship(
                        source_id=source_id,
                        target_id=target_id,
                        rel_type=rel_type,
                        properties=rel_properties
                    )
                    state['processing_log'].append(f"Created relationship in Neo4j: {source_name} -{rel_type}-> {target_name}")
                else:
                    # Fallback to direct Cypher query if IDs not found
                    with neo4j_client.driver.session() as session:
                        result = session.run(f"""
                            MATCH (source:Entity {{name: $source_name, tenant_id: $tenant_id}})
                            MATCH (target:Entity {{name: $target_name, tenant_id: $tenant_id}})
                            MERGE (source)-[r:{rel_type}]->(target)
                            RETURN source.name, target.name, type(r)
                        """, {
                            "source_name": source_name,
                            "target_name": target_name,
                            "tenant_id": tenant_id
                        })
                    
                    # Check if relationship was created
                    record = result.single()
                    if record:
                        state['processing_log'].append(f"Created relationship in Neo4j: {record[0]} -{record[2]}-> {record[1]}")
                    else:
                        state['processing_log'].append(f"Failed to create relationship: {source_name} -{rel_type}-> {target_name}")
                
            except Exception as e:
                logger.error(f"Error creating relationship {relationship.get('type')}: {str(e)}")
                state['processing_log'].append(f"Error creating relationship {relationship.get('type')}: {str(e)}")
                continue
        
        # Update status
        state['status'] = 'neo4j_persisted'
        state['processing_log'].append(f"Successfully persisted entities and relationships to Neo4j")
        state['processing_log'].append(f"Completed persisting to Neo4j at {datetime.now(timezone.utc).isoformat()}")
        
        # Close Neo4j client
        neo4j_client.close()
        
        return state
    
    except Exception as e:
        logger.error(f"Unexpected error in persist_to_neo4j: {str(e)}")
        if 'processing_log' in state:
            state['processing_log'].append(f"Critical error in persisting to Neo4j: {str(e)}")
        state['status'] = 'failed'
        return state