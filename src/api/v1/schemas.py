from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Common schemas
class StatusResponse(BaseModel):
    status: str
    message: str


# Base request with tenant ID
class TenantRequest(BaseModel):
    tenant_id: str = Field(default="default")


# Ingestion schemas
class DocumentMetadata(BaseModel):
    source: str
    author: Optional[str] = None
    created_at: Optional[str] = None 
    document_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestDocumentRequest(TenantRequest):
    """Request model for ingesting document content"""
    content: str
    metadata: Optional[DocumentMetadata] = None


class IngestUrlRequest(TenantRequest):
    """Request model for ingesting content from a URL"""
    url: str
    metadata: Optional[DocumentMetadata] = None


class IngestFileRequest(TenantRequest):
    """Request model for ingesting content from a file"""
    # This will be used with File upload in the API
    metadata: Optional[DocumentMetadata] = None


class IngestResponse(BaseModel):
    """Response model for ingestion endpoints"""
    job_id: str
    status_code: int = Field(default=200)
    status_message: str = Field(default="OK")


class Citation(BaseModel):
    """Model for a citation/source in the response"""
    id: str
    source: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: Optional[float] = None


# Query schemas
class QueryRequest(TenantRequest):
    """Request model for querying the system"""
    query_str: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    top_k: int = Field(default=5, ge=1, le=100)


class Response(BaseModel):
    """Response model for queries"""
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    reasoning: Optional[str] = None
    synthesis: Optional[str] = None


# Legacy schemas (kept for backward compatibility)
class QueryFilters(BaseModel):
    """Filters for the query"""
    tenant_id: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    additional_filters: Dict[str, Any] = Field(default_factory=dict)


class LegacyQueryRequest(BaseModel):
    query: str
    filters: Optional[QueryFilters] = None
    top_k: int = Field(default=5, ge=1, le=100)


class SourceDocument(BaseModel):
    document_id: str
    content: str
    metadata: DocumentMetadata
    relevance_score: float


class LegacyQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceDocument] = Field(default_factory=list)
    reasoning: Optional[str] = None

# Global Knowledge Domain schemas

# AI Tools schemas
class AITool(BaseModel):
    """Model for an AI tool"""
    name: str
    description: str
    use_case: Optional[str] = None
    url: str
    category: Optional[str] = None
    pricing: Optional[str] = None
    reviews: Optional[str] = None
    rating: Optional[float] = None
    tags: Optional[List[str]] = None
    tool_id: str
    relevance_score: Optional[float] = None
    citation_id: Optional[str] = None

class AIToolsSearchRequest(TenantRequest):
    """Request model for searching AI tools"""
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=100)

class AIToolsSearchResponse(BaseModel):
    """Response model for AI tools search"""
    query: str
    tools: List[AITool] = Field(default_factory=list)

# Learning Resources schemas
class LearningResource(BaseModel):
    """Model for a learning resource"""
    resource_id: str
    title: str
    description: str
    source_url: str
    resource_type: str
    categories: Dict[str, Any]
    topics_discussed: List[str]
    target_audience: Dict[str, Any]
    useful_context: List[str]
    content: Dict[str, Any]
    tags: List[str]
    estimated_time: str
    relevance_score: Optional[float] = None
    citation_id: Optional[str] = None

class LearningResourcesSearchRequest(TenantRequest):
    """Request model for searching learning resources"""
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=100)

class LearningResourcesSearchResponse(BaseModel):
    """Response model for learning resources search"""
    query: str
    resources: List[LearningResource] = Field(default_factory=list)

# Ecosystem Partners schemas
class EcosystemPartner(BaseModel):
    """Model for an ecosystem partner"""
    partner_id: str
    name: str
    bio: str
    expertise: List[str] = Field(default_factory=list)
    certifications: Optional[List[str]] = None
    case_studies: Optional[str] = None
    website: Optional[str] = None
    contact_info: Optional[str] = None
    budget_tier: Optional[str] = None
    tags: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    citation_id: Optional[str] = None

class EcosystemPartnersSearchRequest(TenantRequest):
    """Request model for searching ecosystem partners"""
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=100)

class EcosystemPartnersSearchResponse(BaseModel):
    """Response model for ecosystem partners search"""
    query: str
    partners: List[EcosystemPartner] = Field(default_factory=list)

# Global Knowledge Domain Ingestion schemas
class GlobalToolIngestionRequest(TenantRequest):
    """Request model for ingesting an AI tool"""
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

# Learning Resource nested models
class LearningResourceContent(BaseModel):
    """Content model for learning resources"""
    summary: str
    learning_objectives: List[str] = Field(default_factory=list)
    full_text_markdown: str
    video_transcript: Optional[str] = None
    video_url: Optional[str] = None

class LearningResourceCategories(BaseModel):
    """Categories model for learning resources"""
    primary: str
    secondary: List[str] = Field(default_factory=list)

class LearningResourceTargetAudience(BaseModel):
    """Target audience model for learning resources"""
    expertise_level: str
    job_roles: List[str] = Field(default_factory=list)

class LearningResourceTaxonomy(BaseModel):
    """Taxonomy model for learning resources"""
    department: str
    team_task_category: str
    type_category: str

class LearningResourceKPIBenefits(BaseModel):
    """KPI benefits model for learning resources"""
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None

class LearningResourceSubscriptions(BaseModel):
    """Subscription model for learning resources"""
    plan_name: str
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    pricing_model: str
    features_included: List[str] = Field(default_factory=list)

class GlobalLearningResourceIngestionRequest(TenantRequest):
    """Request model for ingesting a learning resource with comprehensive fields"""
    title: str
    description: str
    source_url: str
    resource_type: str
    categories: LearningResourceCategories
    topics_discussed: List[str]
    target_audience: LearningResourceTargetAudience
    useful_context: List[str]
    content: LearningResourceContent
    tags: List[str]
    estimatedTime: str
    platform_name: Optional[str] = None
    platform_logo_url: Optional[str] = None
    associated_tool: Optional[str] = None
    taxonomy: Optional[LearningResourceTaxonomy] = None
    kpi_benefits: Optional[LearningResourceKPIBenefits] = None
    is_paid: Optional[bool] = None
    subscriptions: Optional[LearningResourceSubscriptions] = None
    last_scraped_at: Optional[str] = None

class GlobalEcosystemPartnerIngestionRequest(TenantRequest):
    """Request model for ingesting an ecosystem partner"""
    name: str
    bio: str
    expertise: List[str]
    certifications: Optional[List[str]] = None
    case_studies: Optional[str] = None
    website: Optional[str] = None
    contact_info: Optional[str] = None
    budget_tier: Optional[str] = None
    tags: Optional[List[str]] = None

# Tenant Uploaded Files schemas
class TenantUploadedFile(BaseModel):
    """Model for a tenant uploaded file"""
    file_id: str
    file_name: str
    file_path: str
    content_chunk: str
    organization_id: str
    upload_date: Optional[str] = None
    file_type: Optional[str] = None
    tags: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    citation_id: Optional[str] = None

class TenantUploadedFilesSearchRequest(TenantRequest):
    """Request model for searching tenant uploaded files"""
    query: str
    organization_id: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=100)

class TenantUploadedFilesSearchResponse(BaseModel):
    """Response model for tenant uploaded files search"""
    query: str
    files: List[TenantUploadedFile] = Field(default_factory=list)

# Kernel of Truth schemas
class RelationshipInsight(BaseModel):
    """Model for a relationship insight from the Kernel of Truth"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "graph_database"
    citation_id: str
    query: str

class KernelOfTruthRequest(TenantRequest):
    """Request model for querying the Kernel of Truth"""
    query: str
    max_depth: int = Field(default=3, ge=1, le=5)
    limit: int = Field(default=10, ge=1, le=50)

class KernelOfTruthResponse(BaseModel):
    """Response model for Kernel of Truth queries"""
    query: str
    insights: List[RelationshipInsight] = Field(default_factory=list)


# Planner schemas
class PlannerRequest(BaseModel):
    """Request model for planning a retrieval strategy"""
    query: str
    organization_id: str = Field(default="default")
    tenant_id: str = Field(default="default")


class PlannerResponse(BaseModel):
    """Response model for retrieval strategy planning"""
    original_query: str
    organization_id: str
    plan: str
    retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)
    graph_insights: List[Dict[str, Any]] = Field(default_factory=list)
    final_answer: Optional[str] = None
    error_log: List[str] = Field(default_factory=list)
    collections_to_search: List[str] = Field(default_factory=list)


# Vector Search Tenant Documents schemas
class VectorSearchTenantDocsRequest(BaseModel):
    """Request model for vector searching tenant documents"""
    query: str
    organization_id: str
    tenant_id: str = Field(default="default")
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=100)


class VectorSearchTenantDocsResponse(BaseModel):
    """Response model for vector search tenant documents"""
    query: str
    organization_id: str
    files: List[TenantUploadedFile] = Field(default_factory=list)


# Graph RAG Contextualizer schemas
class GraphInsight(BaseModel):
   """Model for a graph relationship insight from the Graph RAG Contextualizer"""
   content: str
   metadata: Dict[str, Any] = Field(default_factory=dict)
   source: str = "graph_database"
   citation_id: str
   explanation: Optional[str] = None
   inferred_context: Optional[str] = None


class GraphRAGContextualizerRequest(BaseModel):
   """Request model for the Graph RAG Contextualizer"""
   query: str
   organization_id: str = Field(default="default")
   tenant_id: str = Field(default="default")
   retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)


class GraphRAGContextualizerResponse(BaseModel):
   """Response model for the Graph RAG Contextualizer"""
   query: str
   organization_id: str
   graph_insights: List[GraphInsight] = Field(default_factory=list)


# Synthesizer schemas
class SynthesizerRequest(BaseModel):
   """Request model for the Synthesizer"""
   query: str
   organization_id: str = Field(default="default")
   tenant_id: str = Field(default="default")
   retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)
   graph_insights: List[Dict[str, Any]] = Field(default_factory=list)


class SynthesizerResponse(BaseModel):
   """Response model for the Synthesizer"""
   query: str
   organization_id: str
   final_answer: str


# Conditional Edge Router schemas
class ConditionalEdgeRouterRequest(BaseModel):
   """Request model for the Conditional Edge Router"""
   original_query: str
   organization_id: str = Field(default="default")
   tenant_id: str = Field(default="default")
   plan: Optional[str] = None
   retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)
   graph_insights: List[Dict[str, Any]] = Field(default_factory=list)
   final_answer: Optional[str] = None
   error_log: List[str] = Field(default_factory=list)


class ConditionalEdgeRouterResponse(BaseModel):
   """Response model for the Conditional Edge Router"""
   original_query: str
   organization_id: str
   next_node: str
   reason: str
   updated_state: Dict[str, Any]


# GCS File Ingestion schemas
class GCSFileIngestionRequest(TenantRequest):
   """Request model for ingesting a file from Google Cloud Storage"""
   file_id: str
   organization_id: str
   gcs_path: str
   metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class GCSFileIngestionState(BaseModel):
    """Model for the state of GCS file ingestion process"""
    file_id: str
    organization_id: str
    gcs_path: str
    raw_text: Optional[str] = None
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    entities_and_relations: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "pending"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "gcs_path": "gs://bucket/path/to/file.pdf",
                "raw_text": "Sample extracted text content...",
                "chunks": [
                    {
                        "content": "This is the first semantic chunk.",
                        "metadata": {
                            "chunk_id": 0,
                            "chunk_type": "semantic",
                            "semantic_type": "introduction"
                        }
                    },
                    {
                        "content": "This is the second semantic chunk.",
                        "metadata": {
                            "chunk_id": 1,
                            "chunk_type": "semantic",
                            "semantic_type": "concept_explanation"
                        }
                    }
                ],
                "entities_and_relations": [],
                "status": "processing",
                "processing_log": ["Started processing at 2025-10-24T10:00:00Z"]
            }
        }


# Chunking Text API schemas
class ChunkTextRequest(TenantRequest):
    """Request model for chunking text using semantic algorithm"""
    file_id: str
    organization_id: str
    raw_text: str
    gcs_path: Optional[str] = ""
    status: Optional[str] = "processing"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "tenant_id": "default",
                "raw_text": "This is a sample text that needs to be chunked into semantic paragraphs. It contains multiple sentences and ideas that should be grouped together based on their meaning and context. The chunking algorithm will analyze this text and break it into meaningful segments.",
                "status": "processing",
                "processing_log": ["Started chunking at 2025-10-24T11:00:00Z"]
            }
        }


class ChunkTextResponse(BaseModel):
    """Response model for chunking text API"""
    file_id: str
    organization_id: str
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "chunked"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "chunks": [
                    {
                        "content": "This is a sample text that needs to be chunked into semantic paragraphs.",
                        "metadata": {
                            "chunk_id": 0,
                            "chunk_type": "semantic",
                            "semantic_type": "introduction",
                            "chunk_index": 0,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        }
                    },
                    {
                        "content": "It contains multiple sentences and ideas that should be grouped together based on their meaning and context. The chunking algorithm will analyze this text and break it into meaningful segments.",
                        "metadata": {
                            "chunk_id": 1,
                            "chunk_type": "semantic",
                            "semantic_type": "explanation",
                            "chunk_index": 1,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        }
                    }
                ],
                "status": "chunked",
                "processing_log": [
                    "Started chunking at 2025-10-24T11:00:00Z",
                    "Created 2 chunks using AI semantic chunking",
                    "Completed semantic chunking at 2025-10-24T11:00:05Z"
                ]
            }
        }


# Generate Embeddings API schemas
class GenerateEmbeddingsRequest(TenantRequest):
    """Request model for generating embeddings for text chunks"""
    file_id: str
    organization_id: str
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    status: Optional[str] = "processing"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "tenant_id": "default",
                "chunks": [
                    {
                        "content": "This is the first semantic chunk.",
                        "metadata": {
                            "chunk_id": 0,
                            "chunk_type": "semantic",
                            "semantic_type": "introduction",
                            "chunk_index": 0,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        }
                    },
                    {
                        "content": "This is the second semantic chunk.",
                        "metadata": {
                            "chunk_id": 1,
                            "chunk_type": "semantic",
                            "semantic_type": "explanation",
                            "chunk_index": 1,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        }
                    }
                ],
                "status": "processing",
                "processing_log": ["Started embedding generation at 2025-10-24T11:00:00Z"]
            }
        }


class GenerateEmbeddingsResponse(BaseModel):
    """Response model for generating embeddings API"""
    file_id: str
    organization_id: str
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "embedded"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "chunks": [
                    {
                        "content": "This is the first semantic chunk.",
                        "metadata": {
                            "chunk_id": 0,
                            "chunk_type": "semantic",
                            "semantic_type": "introduction",
                            "chunk_index": 0,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        },
                        "vector": [0.021, -0.015, 0.042, 0.036, 0.018, -0.027, 0.031, -0.019, 0.022, 0.033]  # Truncated for brevity
                    },
                    {
                        "content": "This is the second semantic chunk.",
                        "metadata": {
                            "chunk_id": 1,
                            "chunk_type": "semantic",
                            "semantic_type": "explanation",
                            "chunk_index": 1,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        },
                        "vector": [0.018, -0.022, 0.039, 0.041, 0.015, -0.031, 0.029, -0.017, 0.025, 0.036]  # Truncated for brevity
                    }
                ],
                "status": "embedded",
                "processing_log": [
                    "Started embedding generation at 2025-10-24T11:00:00Z",
                    "Generated embeddings for 2 chunks",
                    "Completed embedding generation at 2025-10-24T11:00:05Z"
                ]
            }
        }
# Persist to Weaviate API schemas
class PersistToWeaviateRequest(TenantRequest):
    """Request model for persisting embedded chunks to Weaviate"""
    file_id: str
    organization_id: str
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    status: Optional[str] = "embedded"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "tenant_id": "default",
                "chunks": [
                    {
                        "content": "This is the first semantic chunk.",
                        "metadata": {
                            "chunk_id": 0,
                            "chunk_type": "semantic",
                            "semantic_type": "introduction",
                            "chunk_index": 0,
                            "total_chunks": 2,
                            "file_id": "file-123",
                            "organization_id": "org-456",
                            "chunking_method": "ai_semantic"
                        },
                        "vector": [0.021, -0.015, 0.042, 0.036, 0.018]  # Truncated for brevity
                    }
                ],
                "status": "embedded",
                "processing_log": ["Embedding generation completed at 2025-10-24T11:00:05Z"]
            }
        }


class PersistToWeaviateResponse(BaseModel):
    """Response model for persisting to Weaviate API"""
    file_id: str
    organization_id: str
    status: str = "weaviate_persisted"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "status": "weaviate_persisted",
                "processing_log": [
                    "Started persisting to Weaviate at 2025-10-24T11:00:10Z",
                    "Successfully persisted 2 chunks to Weaviate",
                    "Completed persisting to Weaviate at 2025-10-24T11:00:15Z"
                ]
            }
        }

# Persist to Neo4j API schemas
class PersistToNeo4jRequest(TenantRequest):
    """Request model for persisting entities and relations to Neo4j"""
    file_id: str
    organization_id: str
    entities_and_relations: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = "entities_extracted"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "tenant_id": "default",
                "entities_and_relations": {
                    "entities": [
                        {
                            "id": "entity-1",
                            "name": "John Doe",
                            "type": "PERSON"
                        },
                        {
                            "id": "entity-2",
                            "name": "Acme Corporation",
                            "type": "ORGANIZATION"
                        }
                    ],
                    "relationships": [
                        {
                            "source": "John Doe",
                            "target": "Acme Corporation",
                            "type": "WORKS_FOR"
                        }
                    ]
                },
                "status": "entities_extracted",
                "processing_log": ["Entity extraction completed at 2025-10-24T11:00:05Z"]
            }
        }


class PersistToNeo4jResponse(BaseModel):
    """Response model for persisting to Neo4j API"""
    file_id: str
    organization_id: str
    status: str = "neo4j_persisted"
    processing_log: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file-123",
                "organization_id": "org-456",
                "status": "neo4j_persisted",
                "processing_log": [
                    "Started persisting to Neo4j at 2025-10-24T11:00:10Z",
                    "Created document node in Neo4j with ID: file-123",
                    "Created entity node in Neo4j: John Doe",
                    "Created entity node in Neo4j: Acme Corporation",
                    "Created relationship in Neo4j: John Doe -WORKS_FOR-> Acme Corporation",
                    "Successfully persisted entities and relationships to Neo4j",
                    "Completed persisting to Neo4j at 2025-10-24T11:00:15Z"
                ]
            }
        }

class NoCodeTemplateCategory(BaseModel):
    primary: str
    secondary: List[str] = Field(default_factory=list)

class NoCodeTaxonomy(BaseModel):
    department: str
    team_task_category: str
    type_category: str

class NoCodeTargetAudienceTemplate(BaseModel):
    expertise_level: str
    job_roles: List[str] = Field(default_factory=list)

class NoCodeKPIBenefits(BaseModel):
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None

class NoCodeTemplateIngestionRequest(TenantRequest):
    """Request model for ingesting no-code templates"""
    name: str
    source_url: str
    platform: str
    platform_logo_url: Optional[str] = None
    use_cases: List[str] = Field(default_factory=list)
    short_description: str
    complexity: str
    categories: NoCodeTemplateCategory
    concrete_tasks: List[str] = Field(default_factory=list)
    required_connections: List[str] = Field(default_factory=list)
    taxonomy: NoCodeTaxonomy
    target_audience: NoCodeTargetAudienceTemplate
    kpi_benefits: Optional[NoCodeKPIBenefits] = None
    blueprint_json_url: Optional[str] = None

# Pre-Made Prompts schemas
class Taxonomy(BaseModel):
    department: str
    team_task_category: str
    type_category: str

class TargetAudiencePrompt(BaseModel):
    expertise_level: str
    job_roles: List[str] = Field(default_factory=list)

class KPIBenefits(BaseModel):
    estimated_time_saving: Optional[str] = None
    efficiency_gain_percentage: Optional[int] = None
    cost_reduction: Optional[str] = None
    quality_improvement_metric: Optional[str] = None

class PreMadePromptIngestionRequest(TenantRequest):
    """Request model for ingesting pre-made prompts"""
    name: str
    prompt_body: str
    placeholders: List[str] = Field(default_factory=list)
    associated_tool: str
    concrete_tasks: List[str] = Field(default_factory=list)
    taxonomy: Taxonomy
    target_audience: TargetAudiencePrompt
    kpi_benefits: KPIBenefits
    model_compatibility: List[str] = Field(default_factory=list)
    prompting_technique: str
    tags: List[str] = Field(default_factory=list)