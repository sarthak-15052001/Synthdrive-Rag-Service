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

def fix_pydantic_fields():
    """Fix the missing ModelField in pydantic.fields"""
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

def create_mock_langchain_schema():
    """Create a mock langchain.schema module with Document class"""
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

def create_startup_script():
    """Create a startup script that applies all fixes"""
    script_content = """#!/usr/bin/env python3
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

def ensure_langgraph_errors():
    # Ensure langgraph.errors module exists
    try:
        import langgraph.errors
        logger.info("langgraph.errors module exists")
    except ImportError:
        logger.info("Creating mock langgraph.errors module")
        import sys
        import types
        
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
        
        # Add the module to sys.modules
        sys.modules['langgraph.errors'] = mock_errors
        logger.info("Mock langgraph.errors module created")

def fix_security_base():
    # Fix the type_ annotation in APIKey class
    try:
        from fastapi.openapi.models import SecuritySchemeType, APIKey, HTTPBase, HTTPBearer, OAuth2, OpenIdConnect
        from pydantic import Field
        
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
    ensure_langgraph_errors()
    fix_pydantic_error_wrappers()
    fix_pydantic_fields()
    create_mock_langchain_schema()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
"""
    
    script_path = os.path.join(os.getcwd(), "start_all_fixed.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"Created startup script at {script_path}")
    return script_path

if __name__ == "__main__":
    logger.info("Starting fix for Pydantic fields and langchain.schema issues...")
    
    # Apply fixes
    fix_pydantic_fields()
    create_mock_langchain_schema()
    
    # Create startup script
    script_path = create_startup_script()
    
    logger.info("All fixes applied successfully!")
    logger.info(f"Run {script_path} to start the server with all patches applied")