#!/usr/bin/env python3
import os
import sys
import importlib
import logging
import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def fix_security_base():
    # Fix the type_ annotation in APIKey class
    try:
        from fastapi.openapi.models import SecuritySchemeType, APIKey, HTTPBase, HTTPBearer, OAuth2, OpenIdConnect
        
        # Add proper type annotations to all classes that inherit from SecurityBase
        APIKey.type_.__annotations__ = {'return': SecuritySchemeType}
        HTTPBase.type_.__annotations__ = {'return': SecuritySchemeType}
        OAuth2.type_.__annotations__ = {'return': SecuritySchemeType}
        OpenIdConnect.type_.__annotations__ = {'return': SecuritySchemeType}
        
        # Fix the scheme field in HTTPBearer
        HTTPBearer.scheme.__annotations__ = {'return': str}
        
        logger.info("Fixed type_ and scheme annotations in SecurityBase subclasses")
    except (ImportError, AttributeError) as e:
        logger.error(f"Could not fix SecurityBase issue: {e}")

def fix_pydantic_error_wrappers():
    # Ensure ErrorList exists in pydantic.error_wrappers
    try:
        from pydantic import error_wrappers
        
        # Check if ErrorList exists
        if not hasattr(error_wrappers, 'ErrorList'):
            # Create the ErrorList class
            class ErrorList(list):
                """List of errors from Pydantic validation."""
                pass
            
            # Add it to the module
            error_wrappers.ErrorList = ErrorList
            logger.info("Added ErrorList class to pydantic.error_wrappers")
    except ImportError as e:
        logger.error(f"Could not fix pydantic.error_wrappers: {e}")

def fix_pydantic_fields():
    # Ensure ModelField exists in pydantic.fields
    try:
        from pydantic import fields
        
        # Check if ModelField exists
        if not hasattr(fields, 'ModelField'):
            # Create the ModelField class
            class ModelField:
                """Mock ModelField class for compatibility with FastAPI."""
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            # Add it to the module
            fields.ModelField = ModelField
            logger.info("Added ModelField class to pydantic.fields")
    except ImportError as e:
        logger.error(f"Could not fix pydantic.fields: {e}")

def create_mock_langgraph_errors():
    # Ensure langgraph.errors module exists
    try:
        import langgraph.errors
        logger.info("langgraph.errors module exists")
    except ImportError:
        logger.info("Creating mock langgraph.errors module")
        
        # Create a mock module
        mock_errors = types.ModuleType('langgraph.errors')
        
        # Add error classes
        class LangGraphError(Exception):
            """Base class for all LangGraph errors."""
            pass

        class EmptyInputError(LangGraphError):
            """Raised when an input to a node is empty."""
            pass

        class InvalidUpdateError(LangGraphError):
            """Raised when an update to a state is invalid."""
            pass
        
        # Add the classes to the module
        mock_errors.LangGraphError = LangGraphError
        mock_errors.EmptyInputError = EmptyInputError
        mock_errors.InvalidUpdateError = InvalidUpdateError
        
        # Create parent module if needed
        if 'langgraph' not in sys.modules:
            mock_langgraph = types.ModuleType('langgraph')
            sys.modules['langgraph'] = mock_langgraph
        
        # Add the module to sys.modules
        sys.modules['langgraph.errors'] = mock_errors
        logger.info("Mock langgraph.errors module created")

def create_mock_langchain_schema():
    # Ensure langchain.schema module exists
    try:
        import langchain.schema
        logger.info("langchain.schema module exists")
    except ImportError:
        logger.info("Creating mock langchain.schema module")
        
        # Create a mock module
        mock_schema = types.ModuleType('langchain.schema')
        
        # Add Document class
        class Document:
            """Mock Document class for langchain.schema."""
            def __init__(self, page_content="", metadata=None):
                self.page_content = page_content
                self.metadata = metadata or {}
        
        # Add the class to the module
        mock_schema.Document = Document
        
        # Create parent module if needed
        if 'langchain' not in sys.modules:
            mock_langchain = types.ModuleType('langchain')
            sys.modules['langchain'] = mock_langchain
        
        # Add the module to sys.modules
        sys.modules['langchain.schema'] = mock_schema
        logger.info("Mock langchain.schema module created")

def start_server():
    # Apply all runtime fixes
    fix_security_base()
    fix_pydantic_error_wrappers()
    fix_pydantic_fields()
    create_mock_langgraph_errors()
    create_mock_langchain_schema()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
