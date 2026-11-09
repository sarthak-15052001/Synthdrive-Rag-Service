import sys
import os

# Add the project root to the Python path to fix import issues
sys.path.insert(0, os.path.abspath('.'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.endpoints import ingest, query
from src.core.config import settings
from src.data_stores.postgres_client import PostgresClient
from src.data_stores.weaviate_client import WeaviateClient
from src.data_stores.neo4j_client import Neo4jClient
from src.data_stores.neo4j_graphrag_client import Neo4jGraphRAGClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A RAG service for SynthDrive using OpenAI, Weaviate, and Neo4j",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount the API routers
app.include_router(ingest.router, prefix="/api/v1/rag", tags=["ingestion"])
app.include_router(query.router, prefix="/api/v1/rag", tags=["query"])

@app.get("/")
def read_root():
    return {
        "status": "SynthDrive RAG Service is running",
        "version": settings.VERSION,
        "documentation": "/docs",
    }

# Initialize database clients
@app.on_event("startup")
async def startup_db_clients():
    logger.info("Initializing database clients...")
    
    try:
        # Initialize PostgreSQL client (optional)
        try:
            app.state.postgres_client = PostgresClient(settings.POSTGRES_URI)
            logger.info("PostgreSQL client initialized successfully")
        except Exception as pg_error:
            logger.warning(f"PostgreSQL client initialization failed, continuing without it: {str(pg_error)}")
            # Create a dummy PostgreSQL client that does nothing
            class DummyPostgresClient:
                def add_document(self, *args, **kwargs): pass
                def get_document_by_id(self, *args, **kwargs): return None
                def search_documents(self, *args, **kwargs): return []
                def delete_document(self, *args, **kwargs): return False
                def close(self): pass
            
            app.state.postgres_client = DummyPostgresClient()
        
        # Initialize Weaviate client (optional)
        try:
            logger.info(f"Initializing Weaviate client with URL: {settings.WEAVIATE_URL}")
            app.state.weaviate_client = WeaviateClient(
                weaviate_url=settings.WEAVIATE_URL,
                api_key=settings.WEAVIATE_API_KEY
            )
            logger.info("Weaviate client initialized successfully")
            
            # Test connection by getting schema
            try:
                schema = app.state.weaviate_client.client.schema.get()
                logger.info(f"Successfully connected to Weaviate and retrieved schema with {len(schema.get('classes', []))} classes")
            except Exception as schema_error:
                logger.error(f"Connected to Weaviate but failed to retrieve schema: {str(schema_error)}")
                raise
                
        except Exception as wv_error:
            logger.error(f"Weaviate client initialization failed: {str(wv_error)}")
            import traceback
            logger.error(f"Weaviate connection traceback: {traceback.format_exc()}")
            
            # Create a dummy Weaviate client that does nothing but logs warnings
            class DummyWeaviateClient:
                def create_embedding(self, *args, **kwargs):
                    logger.warning("Using dummy Weaviate client - create_embedding returning dummy data")
                    return [0.0] * 1536  # Return dummy embedding
                    
                def add_document(self, *args, **kwargs):
                    logger.warning("Using dummy Weaviate client - add_document returning dummy ID")
                    return "dummy-id"
                    
                def query_documents(self, *args, **kwargs):
                    logger.warning("Using dummy Weaviate client - query_documents returning empty list")
                    return []
                    
                def close(self):
                    logger.warning("Using dummy Weaviate client - close doing nothing")
                    pass
                    
                def search_ai_tools(self, *args, **kwargs):
                    logger.warning("Using dummy Weaviate client - search_ai_tools returning empty list")
                    return []
                    
                def search_tenant_uploaded_files(self, *args, **kwargs):
                    logger.warning("Using dummy Weaviate client - search_tenant_uploaded_files returning empty list")
                    return []
            
            logger.warning("Using dummy Weaviate client as fallback")
            app.state.weaviate_client = DummyWeaviateClient()
        
        # Initialize Neo4j client (optional)
        try:
            app.state.neo4j_client = Neo4jClient(
                uri=settings.NEO4J_URI,
                user=settings.NEO4J_USER,
                password=settings.NEO4J_PASSWORD
            )
            logger.info("Neo4j client initialized successfully")
        except Exception as neo_error:
            logger.warning(f"Neo4j client initialization failed, continuing without it: {str(neo_error)}")
            # Create a dummy Neo4j client that does nothing
            class DummyNeo4jClient:
                def add_document(self, *args, **kwargs): pass
                def get_document_by_id(self, *args, **kwargs): return None
                def get_related_documents(self, *args, **kwargs): return []
                def search_documents(self, *args, **kwargs): return []
                def close(self): pass
            
            app.state.neo4j_client = DummyNeo4jClient()
        
        # Initialize Neo4j GraphRAG client (preferred)
        try:
            app.state.neo4j_graphrag_client = Neo4jGraphRAGClient(
                uri=settings.NEO4J_URI,
                user=settings.NEO4J_USER,
                password=settings.NEO4J_PASSWORD
            )
            logger.info("Neo4j GraphRAG client initialized successfully")
        except Exception as graphrag_error:
            logger.warning(f"Neo4j GraphRAG client initialization failed, continuing without it: {str(graphrag_error)}")
            app.state.neo4j_graphrag_client = None
        
        logger.info("Database clients initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database clients: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_clients():
    logger.info("Shutting down database clients...")
    
    try:
        # Close PostgreSQL client
        if hasattr(app.state, "postgres_client"):
            try:
                app.state.postgres_client.close()
                logger.info("PostgreSQL client closed successfully")
            except Exception as pg_error:
                logger.warning(f"Error closing PostgreSQL client: {str(pg_error)}")
        
        # Close Weaviate client
        if hasattr(app.state, "weaviate_client"):
            try:
                app.state.weaviate_client.close()
                logger.info("Weaviate client closed successfully")
            except Exception as wv_error:
                logger.warning(f"Error closing Weaviate client: {str(wv_error)}")
        
        # Close Neo4j client
        if hasattr(app.state, "neo4j_client"):
            try:
                app.state.neo4j_client.close()
                logger.info("Neo4j client closed successfully")
            except Exception as neo_error:
                logger.warning(f"Error closing Neo4j client: {str(neo_error)}")
        
        # Close all Neo4j drivers in the connection pool
        try:
            from src.data_stores.neo4j_client import Neo4jClient
            Neo4jClient.close_all_drivers()
            logger.info("All Neo4j drivers closed successfully")
        except Exception as pool_error:
            logger.warning(f"Error closing Neo4j driver pool: {str(pool_error)}")
        
        # Close Neo4j GraphRAG client
        if hasattr(app.state, "neo4j_graphrag_client") and app.state.neo4j_graphrag_client:
            try:
                app.state.neo4j_graphrag_client.close()
                logger.info("Neo4j GraphRAG client closed successfully")
            except Exception as graphrag_error:
                logger.warning(f"Error closing Neo4j GraphRAG client: {str(graphrag_error)}")
        
        logger.info("Database clients shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down database clients: {str(e)}")