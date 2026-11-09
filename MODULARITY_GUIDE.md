# System Modularity Guide: Making Resource Types Extension Easy

## Overview

This document explains how to refactor the SynthDrive RAG service to make it more modular, specifically to enable adding new resource types (like learning resources, tools, ecosystem partners, etc.) without modifying existing code. This follows the **Open-Closed Principle** (open for extension, closed for modification).

## Current Architecture Analysis

### Current State

The system currently handles multiple resource types:
1. **Global Tools** - AI tools catalog
2. **Global Learning Resources** - Educational content
3. **Global Ecosystem Partners** - Partner directory
4. **No-Code Templates** - Automation templates
5. **Pre-Made Prompts** - Prompt library
6. **Tenant Uploaded Files** - Organization-specific documents

### Pain Points

Currently, adding a new resource type requires modifications across multiple files:

1. **[`src/api/v1/schemas.py`](src/api/v1/schemas.py)** - Add new Pydantic schemas
2. **[`src/api/v1/endpoints/ingest.py`](src/api/v1/endpoints/ingest.py)** - Add new endpoint handlers
3. **[`src/ingestion/nodes.py`](src/ingestion/nodes.py)** - Update processing logic with new conditions
4. **[`src/data_stores/weaviate_client.py`](src/data_stores/weaviate_client.py)** - Add new class schema and methods
5. **[`src/data_stores/neo4j_client.py`](src/data_stores/neo4j_client.py)** - Add new graph creation logic

This tight coupling makes the system difficult to extend and maintain.

---

## Proposed Modular Architecture

### 1. Resource Type Registry Pattern

Create a centralized registry that manages all resource types and their configurations.

#### Implementation Structure

```
src/
├── resource_types/
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   ├── registry.py                # Resource type registry
│   ├── implementations/
│   │   ├── __init__.py
│   │   ├── global_tool.py         # Tool resource type
│   │   ├── learning_resource.py   # Learning resource type
│   │   ├── ecosystem_partner.py   # Partner resource type
│   │   ├── no_code_template.py    # Template resource type
│   │   └── pre_made_prompt.py     # Prompt resource type
│   └── plugins/                   # For future custom resource types
```

#### Core Component: Base Resource Type

Create [`src/resource_types/base.py`](src/resource_types/base.py):

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ResourceTypeDefinition(ABC):
    """
    Abstract base class for all resource types.
    Each resource type must implement these methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the resource type (e.g., 'global_tool')"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'AI Tool')"""
        pass
    
    @property
    @abstractmethod
    def ingestion_schema(self) -> type[BaseModel]:
        """Pydantic schema for ingestion requests"""
        pass
    
    @property
    @abstractmethod
    def weaviate_class_name(self) -> str:
        """Weaviate collection name (e.g., 'Global_Tools')"""
        pass
    
    @abstractmethod
    def get_weaviate_schema(self) -> Dict[str, Any]:
        """Return Weaviate class definition"""
        pass
    
    @abstractmethod
    def prepare_for_weaviate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for Weaviate storage"""
        pass
    
    @abstractmethod
    def prepare_for_neo4j(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for Neo4j storage"""
        pass
    
    @abstractmethod
    def create_neo4j_graph(
        self, 
        neo4j_client: Any, 
        data: Dict[str, Any], 
        tenant_id: str
    ) -> None:
        """Create nodes and relationships in Neo4j"""
        pass
    
    @abstractmethod
    def generate_embedding_content(self, data: Dict[str, Any]) -> str:
        """Generate text content for embedding"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate resource-specific requirements"""
        pass
    
    # Optional methods with default implementations
    
    def should_extract_entities(self) -> bool:
        """Whether to extract entities from this resource type"""
        return False
    
    def get_search_properties(self) -> List[str]:
        """Properties to include in search results"""
        return []
    
    def supports_connector(self) -> bool:
        """Whether this resource type has an external connector"""
        return False
    
    def get_connector_client(self) -> Optional[Any]:
        """Get the connector client if supported"""
        return None
```

#### Component: Resource Type Registry

Create [`src/resource_types/registry.py`](src/resource_types/registry.py):

```python
from typing import Dict, Optional
from .base import ResourceTypeDefinition


class ResourceTypeRegistry:
    """
    Central registry for all resource types.
    Implements the Singleton pattern.
    """
    
    _instance = None
    _resource_types: Dict[str, ResourceTypeDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, resource_type: ResourceTypeDefinition) -> None:
        """Register a new resource type"""
        name = resource_type.name
        if name in self._resource_types:
            raise ValueError(f"Resource type '{name}' is already registered")
        
        self._resource_types[name] = resource_type
        print(f"✓ Registered resource type: {resource_type.display_name}")
    
    def get(self, name: str) -> Optional[ResourceTypeDefinition]:
        """Get a resource type by name"""
        return self._resource_types.get(name)
    
    def get_all(self) -> Dict[str, ResourceTypeDefinition]:
        """Get all registered resource types"""
        return self._resource_types.copy()
    
    def list_names(self) -> List[str]:
        """List all registered resource type names"""
        return list(self._resource_types.keys())
    
    def is_registered(self, name: str) -> bool:
        """Check if a resource type is registered"""
        return name in self._resource_types


# Global registry instance
registry = ResourceTypeRegistry()
```

---

### 2. Example Resource Type Implementation

Create [`src/resource_types/implementations/global_tool.py`](src/resource_types/implementations/global_tool.py):

```python
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import uuid

from ..base import ResourceTypeDefinition
from src.data_stores.global_tools_client import GlobalToolsClient, GlobalTool


class GlobalToolIngestionSchema(BaseModel):
    """Pydantic schema for tool ingestion"""
    name: str
    homepage_url: str
    last_scraped_at: Optional[str] = None
    source_urls: List[str]
    categories: Dict[str, Any]
    short_description: str
    detailed_description: str
    features: List[Dict[str, str]]
    differentiators: List[str]
    subscriptions: List[Dict[str, Any]]
    compliance: Dict[str, Any]
    documentation_links: List[str]
    rating: float
    logo_url: Optional[str] = None
    tags: List[str]


class GlobalToolResourceType(ResourceTypeDefinition):
    """Resource type definition for AI Tools"""
    
    @property
    def name(self) -> str:
        return "global_tool"
    
    @property
    def display_name(self) -> str:
        return "AI Tool"
    
    @property
    def ingestion_schema(self) -> type[BaseModel]:
        return GlobalToolIngestionSchema
    
    @property
    def weaviate_class_name(self) -> str:
        return "Global_Tools"
    
    def get_weaviate_schema(self) -> Dict[str, Any]:
        """Return Weaviate class definition for tools"""
        return {
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
                {"name": "name", "dataType": ["string"]},
                {"name": "homepage_url", "dataType": ["string"]},
                {"name": "last_scraped_at", "dataType": ["date"]},
                {"name": "source_urls", "dataType": ["string[]"]},
                {"name": "categories_json", "dataType": ["text"]},
                {"name": "short_description", "dataType": ["text"]},
                {"name": "detailed_description", "dataType": ["text"]},
                {"name": "features_json", "dataType": ["text"]},
                {"name": "differentiators", "dataType": ["text[]"]},
                {"name": "subscriptions_json", "dataType": ["text"]},
                {"name": "compliance_json", "dataType": ["text"]},
                {"name": "documentation_links", "dataType": ["string[]"]},
                {"name": "rating", "dataType": ["number"]},
                {"name": "logo_url", "dataType": ["string"]},
                {"name": "tags", "dataType": ["string[]"]},
                {"name": "tenant_id", "dataType": ["string"]},
                {"name": "content", "dataType": ["text"]}
            ]
        }
    
    def prepare_for_weaviate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform tool data for Weaviate storage"""
        categories = data.get('categories', {})
        features = data.get('features', [])
        subscriptions = data.get('subscriptions', [])
        compliance = data.get('compliance', {})
        
        return {
            "name": data.get('name', ''),
            "homepage_url": data.get('homepage_url', ''),
            "last_scraped_at": self._format_date(data.get('last_scraped_at')),
            "source_urls": data.get('source_urls', []),
            "categories_json": json.dumps(categories),
            "short_description": data.get('short_description', ''),
            "detailed_description": data.get('detailed_description', ''),
            "features_json": json.dumps(features),
            "differentiators": data.get('differentiators', []),
            "subscriptions_json": json.dumps(subscriptions),
            "compliance_json": json.dumps(compliance),
            "documentation_links": data.get('documentation_links', []),
            "rating": data.get('rating', 0.0),
            "logo_url": data.get('logo_url', ''),
            "tags": data.get('tags', [])
        }
    
    def prepare_for_neo4j(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform tool data for Neo4j storage"""
        return {
            "tool_id": data.get("tool_id", str(uuid.uuid4())),
            "name": data.get("name", ""),
            "homepage_url": data.get("homepage_url", ""),
            "categories": data.get("categories", {}),
            "features": data.get("features", []),
            "tags": data.get("tags", [])
        }
    
    def create_neo4j_graph(
        self, 
        neo4j_client: Any, 
        data: Dict[str, Any], 
        tenant_id: str
    ) -> None:
        """Create tool nodes and relationships in Neo4j"""
        neo4j_data = self.prepare_for_neo4j(data)
        tool_id = neo4j_data["tool_id"]
        categories = neo4j_data["categories"]
        
        # Create Tool node
        neo4j_client.query("""
            CREATE (t:Tool {
                tool_id: $tool_id,
                name: $name,
                homepage_url: $homepage_url,
                tenant_id: $tenant_id
            })
        """, {
            "tool_id": tool_id,
            "name": neo4j_data["name"],
            "homepage_url": neo4j_data["homepage_url"],
            "tenant_id": tenant_id
        })
        
        # Create Category nodes and relationships
        primary = categories.get("primary", "")
        if primary:
            neo4j_client.query("""
                MERGE (c:Category {name: $category, tenant_id: $tenant_id})
                WITH c
                MATCH (t:Tool {tool_id: $tool_id})
                MERGE (t)-[:HAS_PRIMARY_CATEGORY]->(c)
            """, {"category": primary, "tool_id": tool_id, "tenant_id": tenant_id})
        
        # Create Feature nodes
        for feature in neo4j_data["features"]:
            neo4j_client.query("""
                MERGE (f:Feature {
                    name: $name,
                    tenant_id: $tenant_id
                })
                WITH f
                MATCH (t:Tool {tool_id: $tool_id})
                MERGE (t)-[:HAS_FEATURE]->(f)
            """, {
                "name": feature.get("name", ""),
                "tool_id": tool_id,
                "tenant_id": tenant_id
            })
    
    def generate_embedding_content(self, data: Dict[str, Any]) -> str:
        """Generate combined content for embedding"""
        content = f"Tool name: {data.get('name', '')}\n"
        content += f"Short description: {data.get('short_description', '')}\n"
        content += f"Detailed description: {data.get('detailed_description', '')}\n"
        
        categories = data.get('categories', {})
        content += f"Primary category: {categories.get('primary', '')}\n"
        content += f"Secondary categories: {', '.join(categories.get('secondary', []))}\n"
        
        for feature in data.get('features', []):
            content += f"- {feature.get('name')}: {feature.get('description')}\n"
        
        return content
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate tool-specific requirements"""
        if not data.get('name'):
            raise ValueError("Tool name is required")
        if not data.get('short_description'):
            raise ValueError("Short description is required")
        if not data.get('categories', {}).get('primary'):
            raise ValueError("Primary category is required")
    
    def supports_connector(self) -> bool:
        return True
    
    def get_connector_client(self) -> Optional[Any]:
        return GlobalToolsClient()
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date to RFC3339"""
        if not date_str:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

---

### 3. Refactored Ingestion Pipeline

#### Unified Ingestion Endpoint

Create [`src/api/v1/endpoints/resource_ingestion.py`](src/api/v1/endpoints/resource_ingestion.py):

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Annotated
from uuid import uuid4
import logging

from src.resource_types.registry import registry
from src.api.dependencies import get_ingestion_graph, get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest/{resource_type}", tags=["ingestion"])
async def ingest_resource(
    resource_type: str,
    request_data: Dict[str, Any],
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)],
    ingestion_graph: Annotated[Any, Depends(get_ingestion_graph)]
):
    """
    Universal ingestion endpoint for any registered resource type.
    
    Args:
        resource_type: The type of resource (e.g., 'global_tool', 'learning_resource')
        request_data: The resource data matching the resource type's schema
        current_user: Authenticated user
        ingestion_graph: The ingestion graph instance
    """
    logger.info(f"Ingesting resource type: {resource_type}")
    
    # Get resource type definition from registry
    resource_def = registry.get(resource_type)
    if not resource_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource type '{resource_type}' not found. Available types: {registry.list_names()}"
        )
    
    try:
        # Validate against the resource type's schema
        schema_class = resource_def.ingestion_schema
        validated_data = schema_class(**request_data)
        
        # Additional resource-specific validation
        resource_def.validate_data(validated_data.model_dump())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    
    # Generate job ID
    job_id = str(uuid4())
    
    try:
        # Convert to dict for processing
        data = validated_data.model_dump()
        
        # Add metadata
        data["source_type"] = resource_type
        data["document_type"] = resource_type
        
        # Generate embedding content
        content = resource_def.generate_embedding_content(data)
        
        # Prepare input for ingestion graph
        input_data = {
            "content": content,
            "metadata": data,
            "job_id": job_id,
            "source_type": resource_type,
            "resource_definition": resource_def
        }
        
        # Send to connector if supported
        if resource_def.supports_connector():
            connector_client = resource_def.get_connector_client()
            if connector_client:
                try:
                    await connector_client.send_data(data)
                    logger.info(f"Sent {resource_type} to external connector")
                except Exception as e:
                    logger.warning(f"Connector failed: {str(e)}, continuing with local ingestion")
        
        # Start async ingestion
        result = await ingestion_graph.ingest_document_async(
            input_data=input_data,
            tenant_id=data.get("tenant_id", "default")
        )
        
        if isinstance(result, Exception):
            raise result
        
        logger.info(f"{resource_def.display_name} ingestion started with job ID: {job_id}")
        
        return {
            "job_id": job_id,
            "status_code": 200,
            "status_message": f"{resource_def.display_name} ingestion started successfully",
            "resource_type": resource_type
        }
        
    except Exception as e:
        logger.error(f"Error ingesting {resource_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest {resource_type}: {str(e)}"
        )
```

#### Refactored Ingestion Nodes

Update [`src/ingestion/nodes.py`](src/ingestion/nodes.py) with a generic processor:

```python
from src.resource_types.registry import registry


def store_in_weaviate(
    processed_chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    tenant_id: str,
    weaviate_client: WeaviateClient
) -> None:
    """
    Generic Weaviate storage using resource type definitions.
    """
    if not processed_chunks or not embeddings:
        logger.warning("No chunks or embeddings to store")
        return
    
    try:
        for i, (chunk, embedding) in enumerate(zip(processed_chunks, embeddings)):
            metadata = chunk.get("metadata", {})
            source_type = metadata.get("source_type", "")
            
            # Get resource definition from registry
            resource_def = registry.get(source_type)
            
            if resource_def:
                # Use resource-specific transformation
                weaviate_data = resource_def.prepare_for_weaviate(metadata)
                weaviate_data["content"] = chunk["content"]
                weaviate_data["tenant_id"] = tenant_id
                
                # Add to Weaviate
                weaviate_client.add_object(
                    collection_name=resource_def.weaviate_class_name,
                    data_object=weaviate_data,
                    vector=embedding
                )
                
                logger.info(f"Added {resource_def.display_name} to {resource_def.weaviate_class_name}")
            else:
                # Fallback to generic storage
                weaviate_client.add_document(
                    content=chunk["content"],
                    metadata=metadata,
                    embedding=embedding
                )
    except Exception as e:
        logger.error(f"Error storing in Weaviate: {str(e)}")
        raise


def store_in_neo4j(
    processed_chunks: List[Dict[str, Any]],
    entities: Dict[str, Any],
    tenant_id: str,
    neo4j_client: Neo4jClient
) -> None:
    """
    Generic Neo4j storage using resource type definitions.
    """
    if not processed_chunks:
        return
    
    try:
        metadata = processed_chunks[0].get("metadata", {})
        source_type = metadata.get("source_type", "")
        
        # Get resource definition from registry
        resource_def = registry.get(source_type)
        
        if resource_def:
            # Use resource-specific graph creation
            resource_def.create_neo4j_graph(
                neo4j_client=neo4j_client,
                data=metadata,
                tenant_id=tenant_id
            )
            logger.info(f"Created Neo4j graph for {resource_def.display_name}")
        else:
            # Fallback to entity-based storage
            store_entities_in_neo4j(processed_chunks, entities, tenant_id, neo4j_client)
    except Exception as e:
        logger.error(f"Error storing in Neo4j: {str(e)}")
        raise
```

#### Refactored Weaviate Client

Update [`src/data_stores/weaviate_client.py`](src/data_stores/weaviate_client.py):

```python
from src.resource_types.registry import registry


class WeaviateClient:
    def __init__(self, weaviate_url: Optional[str] = None, api_key: Optional[str] = None):
        # ... existing initialization ...
        
        # Create schemas from registry
        self.create_schemas_from_registry()
    
    def create_schemas_from_registry(self):
        """Create Weaviate schemas for all registered resource types"""
        try:
            schema = self.client.schema.get()
            existing_classes = [cls.get("class") for cls in schema.get("classes", [])]
            
            # Iterate through all registered resource types
            for resource_type in registry.get_all().values():
                class_name = resource_type.weaviate_class_name
                
                if class_name not in existing_classes:
                    logging.info(f"Creating Weaviate class: {class_name}")
                    class_obj = resource_type.get_weaviate_schema()
                    self.client.schema.create_class(class_obj)
                    logging.info(f"✓ Created {class_name} for {resource_type.display_name}")
        except Exception as e:
            logging.error(f"Error creating schemas from registry: {str(e)}")
            raise
    
    def add_object(
        self, 
        collection_name: str, 
        data_object: Dict[str, Any],
        vector: List[float]
    ) -> str:
        """Generic method to add any resource type to Weaviate"""
        try:
            obj_id = self.client.data_object.create(
                class_name=collection_name,
                data_object=data_object,
                vector=vector
            )
            logging.info(f"Added object to {collection_name} with ID: {obj_id}")
            return obj_id
        except Exception as e:
            logging.error(f"Error adding object to {collection_name}: {str(e)}")
            raise
```

---

### 4. Automatic Resource Type Discovery

Create [`src/resource_types/__init__.py`](src/resource_types/__init__.py):

```python
"""
Resource Types Module

This module auto-discovers and registers all resource type implementations.
To add a new resource type, simply create a new file in implementations/
and define a class that inherits from ResourceTypeDefinition.
"""

import os
import importlib
import inspect
from pathlib import Path

from .registry import registry
from .base import ResourceTypeDefinition


def auto_register_resource_types():
    """
    Automatically discover and register all resource type implementations.
    """
    implementations_dir = Path(__file__).parent / "implementations"
    
    if not implementations_dir.exists():
        return
    
    # Iterate through all Python files in implementations/
    for file_path in implementations_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue
        
        module_name = f"src.resource_types.implementations.{file_path.stem}"
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find all ResourceTypeDefinition subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, ResourceTypeDefinition) and 
                    obj is not ResourceTypeDefinition and
                    not inspect.isabstract(obj)):
                    
                    # Instantiate and register
                    instance = obj()
                    registry.register(instance)
                    
        except Exception as e:
            print(f"⚠ Error loading resource type from {file_path.name}: {str(e)}")


# Auto-register all resource types on module import
auto_register_resource_types()


# Export registry for external use
__all__ = ['registry', 'ResourceTypeDefinition']
```

---

## Adding a New Resource Type - Step-by-Step Guide

### Step 1: Create Resource Class

Create a new file in [`src/resource_types/implementations/`](src/resource_types/implementations/):

```python
# src/resource_types/implementations/my_new_resource.py

from typing import Dict, Any
from pydantic import BaseModel
from ..base import ResourceTypeDefinition


class MyNewResourceSchema(BaseModel):
    """Schema for your new resource"""
    name: str
    description: str
    # ... other fields


class MyNewResourceType(ResourceTypeDefinition):
    """Your new resource type implementation"""
    
    @property
    def name(self) -> str:
        return "my_new_resource"
    
    @property
    def display_name(self) -> str:
        return "My New Resource"
    
    @property
    def ingestion_schema(self) -> type[BaseModel]:
        return MyNewResourceSchema
    
    @property
    def weaviate_class_name(self) -> str:
        return "MyNewResources"
    
    def get_weaviate_schema(self) -> Dict[str, Any]:
        return {
            "class": "MyNewResources",
            # ... schema definition
        }
    
    def prepare_for_weaviate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": data.get("name"),
            "description": data.get("description"),
            # ... transform data
        }
    
    def prepare_for_neo4j(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"name": data.get("name")}
    
    def create_neo4j_graph(self, neo4j_client, data, tenant_id):
        # Create nodes and relationships
        pass
    
    def generate_embedding_content(self, data: Dict[str, Any]) -> str:
        return f"Name: {data.get('name')}\nDescription: {data.get('description')}"
    
    def validate_data(self, data: Dict[str, Any]) -> None:
        if not data.get("name"):
            raise ValueError("Name is required")
```

### Step 2: Restart Application

That's it! The resource type will be automatically discovered and registered on application startup.

### Step 3: Use the Resource Type

```bash
# Ingest using the universal endpoint
POST /rag/ingest/my_new_resource
{
  "name": "Example Resource",
  "description": "This is a test",
  ...
}

# Search using the universal search endpoint
GET /rag/search/my_new_resource?q=example
```

---

## Benefits of This Architecture

### 1. **Open-Closed Principle**
- ✅ Open for extension (add new resource types easily)
- ✅ Closed for modification (no changes to core code)

### 2. **Single Responsibility**
- Each resource type manages its own:
  - Schema definition
  - Validation logic
  - Data transformation
  - Storage strategies

### 3. **Reduced Code Duplication**
- Generic ingestion pipeline
- Reusable storage methods
- Common validation framework

### 4. **Improved Testability**
- Each resource type can be tested independently
- Mock resource types for testing
- Isolated unit tests

### 5. **Better Maintainability**
- Clear separation of concerns
- Easy to locate resource-specific logic
- Self-documenting code structure

### 6. **Plugin Architecture Ready**
- External plugins can add resource types
- No core code changes needed
- Dynamic discovery mechanism

---

## Migration Path

### Phase 1: Create Base Infrastructure
1. Create [`src/resource_types/`](src/resource_types/) directory structure
2. Implement [`base.py`](src/resource_types/base.py) and [`registry.py`](src/resource_types/registry.py)
3. Add auto-discovery mechanism

### Phase 2: Migrate Existing Resource Types
1. Convert Global Tools to new pattern
2. Convert Learning Resources
3. Convert Ecosystem Partners
4. Convert remaining types

### Phase 3: Refactor Core Components
1. Update [`ingestion/nodes.py`](src/ingestion/nodes.py) to use registry
2. Update [`weaviate_client.py`](src/data_stores/weaviate_client.py)
3. Update [`neo4j_client.py`](src/data_stores/neo4j_client.py)
4. Create unified API endpoints

### Phase 4: Deprecate Old Endpoints
1. Mark old endpoints as deprecated
2. Add deprecation warnings
3. Update documentation
4. Remove after transition period

---

## Advanced Features

### 1. Resource Type Dependencies

```python
class ResourceTypeDefinition(ABC):
    def get_dependencies(self) -> List[str]:
        """Return list of resource types this depends on"""
        return []
```

### 2. Custom Search Strategies

```python
class ResourceTypeDefinition(ABC):
    def get_search_strategy(self) -> Optional[SearchStrategy]:
        """Return custom search strategy if needed"""
        return None
```

### 3. Validation Hooks

```python
class ResourceTypeDefinition(ABC):
    def pre_storage_hook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before storage"""
        return data
    
    def post_storage_hook(self, data: Dict[str, Any], storage_ids: Dict[str, str]) -> None:
        """Hook called after successful storage"""
        pass
```

### 4. Resource Type Metadata

```python
class ResourceTypeDefinition(ABC):
    @property
    def version(self) -> str:
        """Resource type version for migrations"""
        return "1.0.0"
    
    @property
    def tags(self) -> List[str]:
        """Categorization tags"""
        return []
```

---

## Example: Complete Implementation

See the example implementation in [`src/resource_types/implementations/global_tool.py`](src/resource_types/implementations/global_tool.py) for a complete, production-ready resource type.

---

## Conclusion

This modular architecture transforms the system from a tightly-coupled design to a flexible, extensible platform. New resource types can be added by:

1. Creating a single Python file
2. Implementing the `ResourceTypeDefinition` interface
3. Letting the auto-discovery mechanism handle registration

**No modifications to existing code required!**

This approach scales well as the system grows and makes it easy for multiple teams to work independently on different resource types.
