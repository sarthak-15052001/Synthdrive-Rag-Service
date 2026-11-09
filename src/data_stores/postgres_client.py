from sqlalchemy import create_engine, Column, String, Integer, Text, JSON, DateTime, MetaData, Table, select, insert, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from src.core.config import settings

# Create base class for declarative models
Base = declarative_base()


class Document(Base):
    """
    SQLAlchemy model for documents.
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    doc_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid conflict with SQLAlchemy


class PostgresClient:
    """
    Client for interacting with PostgreSQL database.
    """

    def __init__(self, db_uri: str = None):
        """
        Initialize the PostgreSQL client.
        
        Args:
            db_uri: URI of the PostgreSQL database
        """
        self.db_uri = db_uri or settings.POSTGRES_URI
        
        # Initialize SQLAlchemy engine and session
        self.engine = create_engine(self.db_uri)
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        """
        Create tables if they don't exist.
        """
        Base.metadata.create_all(self.engine)

    def add_document(self, document_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """
        Add a document to the database.
        
        Args:
            document_id: The ID of the document
            content: The content of the document
            metadata: Metadata about the document
        """
        with self.Session() as session:
            # Check if document already exists
            existing = session.query(Document).filter(Document.id == document_id).first()
            
            if existing:
                # Update existing document
                existing.content = content
                existing.source = metadata.get("source", "unknown")
                existing.doc_metadata = metadata
            else:
                # Create new document
                document = Document(
                    id=document_id,
                    content=content,
                    source=metadata.get("source", "unknown"),
                    doc_metadata=metadata
                )
                session.add(document)
            
            session.commit()

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document from the database by ID.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            The document or None if not found
        """
        with self.Session() as session:
            document = session.query(Document).filter(Document.id == document_id).first()
            
            if document:
                return {
                    "id": document.id,
                    "content": document.content,
                    "source": document.source,
                    "created_at": document.created_at.isoformat() if document.created_at else None,
                    "metadata": document.doc_metadata
                }
            
            return None

    def search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents in the database.
        
        Args:
            query: The search query
            filters: Optional filters to apply
            limit: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        with self.Session() as session:
            # Build the query
            stmt = select(Document)
            
            # Add full-text search condition
            # Note: This is a simplified implementation
            # In a real application, you would use PostgreSQL's full-text search capabilities
            if query:
                stmt = stmt.where(Document.content.ilike(f"%{query}%"))
            
            # Add filters if provided
            if filters:
                if "source" in filters:
                    stmt = stmt.where(Document.source == filters["source"])
            
            # Add limit
            stmt = stmt.limit(limit)
            
            # Execute the query
            result = session.execute(stmt)
            
            # Process the results
            documents = []
            for row in result:
                document = row[0]  # Get the Document object
                documents.append({
                    "id": document.id,
                    "content": document.content,
                    "source": document.source,
                    "created_at": document.created_at.isoformat() if document.created_at else None,
                    "metadata": document.doc_metadata
                })
            
            return documents

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the database.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            True if the document was deleted, False otherwise
        """
        with self.Session() as session:
            document = session.query(Document).filter(Document.id == document_id).first()
            
            if document:
                session.delete(document)
                session.commit()
                return True
            
            return False

    def close(self):
        """
        Close the database connection.
        """
        if self.engine:
            self.engine.dispose()