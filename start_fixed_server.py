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

def start_server():
    # Apply all runtime fixes
    fix_security_base()
    ensure_langgraph_errors()
    fix_pydantic_error_wrappers()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
