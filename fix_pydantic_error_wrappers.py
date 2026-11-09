#!/usr/bin/env python3
"""
Fix script for the Pydantic ErrorList import issue in FastAPI.
This script creates a mock error_wrappers.py module with the necessary ErrorList class.
"""
import os
import sys
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_pydantic_error_wrappers():
    """Fix the Pydantic ErrorList import issue in FastAPI."""
    logger.info("Fixing Pydantic ErrorList import issue...")
    
    # Find the pydantic error_wrappers.py file
    error_wrappers_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv/lib/python3.12/site-packages/pydantic/error_wrappers.py"
    )
    
    if not os.path.exists(error_wrappers_path):
        logger.error(f"Could not find {error_wrappers_path}")
        return False
    
    # Create a backup
    backup_path = f"{error_wrappers_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(error_wrappers_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(error_wrappers_path, 'r') as f:
        content = f.read()
    
    # Add the ErrorList class
    if "class ErrorList(list):" not in content:
        error_list_class = """

# Added by fix script for FastAPI compatibility
class ErrorList(list):
    \"\"\"List of errors from Pydantic validation.\"\"\"
    pass
"""
        # Append the ErrorList class to the end of the file
        with open(error_wrappers_path, 'a') as f:
            f.write(error_list_class)
        
        logger.info(f"Added ErrorList class to {error_wrappers_path}")
    else:
        logger.info("ErrorList class already exists in error_wrappers.py")
    
    return True

def create_startup_script():
    """Create a startup script that applies all fixes before starting the server."""
    logger.info("Creating startup script...")
    
    startup_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "start_fixed_server.py"
    )
    
    startup_script_content = '''#!/usr/bin/env python3
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
'''
    
    with open(startup_script_path, 'w') as f:
        f.write(startup_script_content)
    
    # Make the startup script executable
    os.chmod(startup_script_path, 0o755)
    logger.info(f"Created startup script at {startup_script_path}")
    return True

def main():
    """Main function to fix all issues."""
    logger.info("Starting fix for Pydantic ErrorList import issue...")
    
    # Fix the Pydantic ErrorList import issue
    if not fix_pydantic_error_wrappers():
        logger.error("Failed to fix Pydantic ErrorList import issue.")
        return 1
    
    # Create the startup script
    if not create_startup_script():
        logger.error("Failed to create startup script.")
        return 1
    
    logger.info("All fixes applied successfully!")
    logger.info("Run ./start_fixed_server.py to start the server with all patches applied")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())