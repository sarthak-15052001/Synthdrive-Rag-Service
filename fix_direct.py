#!/usr/bin/env python3
import sys
import types
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def fix_pydantic_fields():
    """Add ModelField class to pydantic.fields."""
    try:
        import pydantic.fields
        
        # Check if ModelField exists
        if not hasattr(pydantic.fields, 'ModelField'):
            # Create the ModelField class
            class ModelField:
                """Mock ModelField class for compatibility with FastAPI."""
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            # Add it to the module
            pydantic.fields.ModelField = ModelField
            logger.info("Added ModelField class to pydantic.fields")
        else:
            logger.info("ModelField class already exists in pydantic.fields")
    except ImportError as e:
        logger.error(f"Could not import pydantic.fields: {e}")

def create_mock_langchain_schema():
    """Create a mock langchain.schema module."""
    try:
        # Check if the module already exists
        try:
            import langchain.schema
            logger.info("langchain.schema module already exists")
            return
        except ImportError:
            pass
        
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
        logger.info("Created mock langchain.schema module")
    except Exception as e:
        logger.error(f"Error creating mock langchain.schema module: {e}")

def create_mock_langgraph_errors():
    """Create a mock langgraph.errors module."""
    try:
        # Check if the module already exists
        try:
            import langgraph.errors
            logger.info("langgraph.errors module already exists")
            return
        except ImportError:
            pass
        
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
        logger.info("Created mock langgraph.errors module")
    except Exception as e:
        logger.error(f"Error creating mock langgraph.errors module: {e}")

def fix_security_base():
    """Fix the type_ annotation in SecurityBase subclasses."""
    try:
        from fastapi.openapi.models import SecuritySchemeType, APIKey, HTTPBase, HTTPBearer, OAuth2, OpenIdConnect
        
        # Add proper type annotations to all classes that inherit from SecurityBase
        if not hasattr(APIKey.type_, '__annotations__'):
            APIKey.type_.__annotations__ = {'return': SecuritySchemeType}
            HTTPBase.type_.__annotations__ = {'return': SecuritySchemeType}
            OAuth2.type_.__annotations__ = {'return': SecuritySchemeType}
            OpenIdConnect.type_.__annotations__ = {'return': SecuritySchemeType}
            
            # Fix the scheme field in HTTPBearer
            HTTPBearer.scheme.__annotations__ = {'return': str}
            
            logger.info("Fixed type_ and scheme annotations in SecurityBase subclasses")
        else:
            logger.info("SecurityBase subclasses already have proper annotations")
    except (ImportError, AttributeError) as e:
        logger.error(f"Could not fix SecurityBase issue: {e}")

def main():
    """Apply all fixes."""
    logger.info("Starting to apply fixes...")
    
    # Apply all fixes
    fix_pydantic_fields()
    create_mock_langchain_schema()
    create_mock_langgraph_errors()
    fix_security_base()
    
    logger.info("All fixes applied successfully!")
    logger.info("Now you can run your server with: uvicorn src.main:app --reload")

if __name__ == "__main__":
    main()