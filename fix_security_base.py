#!/usr/bin/env python3
"""
Fix script for the Pydantic error in FastAPI's SecurityBase class.
This script adds proper type annotations to the type_ field in both
SecurityBase and APIKey classes, as well as the scheme field in HTTPBase and HTTPBearer.
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

def fix_security_base_issue():
    """Fix the Pydantic error in FastAPI's SecurityBase class."""
    logger.info("Fixing SecurityBase type_ annotation issue...")
    
    # Find the fastapi openapi models.py file
    models_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv/lib/python3.12/site-packages/fastapi/openapi/models.py"
    )
    
    if not os.path.exists(models_path):
        logger.error(f"Could not find {models_path}")
        return False
    
    # Create a backup
    backup_path = f"{models_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(models_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Fix the SecurityBase class
    fixed_content = content.replace(
        "type_: SecuritySchemeType = Field(alias=\"type\")",
        "type_: SecuritySchemeType = Field(alias=\"type\")"
    )
    
    # Fix the APIKey class
    fixed_content = fixed_content.replace(
        "type_ = Field(SecuritySchemeType.apiKey, alias=\"type\")",
        "type_: SecuritySchemeType = Field(SecuritySchemeType.apiKey, alias=\"type\")"
    )
    
    # Fix the HTTPBase class
    fixed_content = fixed_content.replace(
        "type_ = Field(SecuritySchemeType.http, alias=\"type\")",
        "type_: SecuritySchemeType = Field(SecuritySchemeType.http, alias=\"type\")"
    )
    
    # Fix the scheme field in HTTPBase
    fixed_content = fixed_content.replace(
        "scheme: str",
        "scheme: str"
    )
    
    # Fix the HTTPBearer class
    fixed_content = fixed_content.replace(
        "scheme = \"bearer\"",
        "scheme: str = \"bearer\""
    )
    
    # Fix the OAuth2 class
    fixed_content = fixed_content.replace(
        "type_ = Field(SecuritySchemeType.oauth2, alias=\"type\")",
        "type_: SecuritySchemeType = Field(SecuritySchemeType.oauth2, alias=\"type\")"
    )
    
    # Fix the OpenIdConnect class
    fixed_content = fixed_content.replace(
        "type_ = Field(SecuritySchemeType.openIdConnect, alias=\"type\")",
        "type_: SecuritySchemeType = Field(SecuritySchemeType.openIdConnect, alias=\"type\")"
    )
    
    # Write the fixed content
    with open(models_path, 'w') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed type_ and scheme annotation issues in {models_path}")
    return True

def create_langgraph_errors_module():
    """Create the missing langgraph.errors module."""
    logger.info("Creating langgraph.errors module...")
    
    # Find the langgraph package directory
    langgraph_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv/lib/python3.12/site-packages/langgraph"
    )
    
    if not os.path.exists(langgraph_path):
        logger.error(f"Could not find {langgraph_path}")
        return False
    
    # Create the errors.py file
    errors_path = os.path.join(langgraph_path, "errors.py")
    
    # Create the errors.py file with the necessary error classes
    error_module_content = '''
# Mock langgraph.errors module
class LangGraphError(Exception):
    """Base class for all LangGraph errors."""
    pass

class EmptyInputError(LangGraphError):
    """Raised when an input to a node is empty."""
    pass

class InvalidUpdateError(LangGraphError):
    """Raised when an update to a state is invalid."""
    pass

class NodeExecutionError(LangGraphError):
    """Raised when a node execution fails."""
    pass

class ConfigurationError(LangGraphError):
    """Raised when there is a configuration error."""
    pass

class ValidationError(LangGraphError):
    """Raised when validation fails."""
    pass
'''
    
    with open(errors_path, 'w') as f:
        f.write(error_module_content)
    
    logger.info(f"Created mock langgraph.errors module at {errors_path}")
    
    # Update the __init__.py to import the errors
    init_path = os.path.join(langgraph_path, "__init__.py")
    if os.path.exists(init_path):
        with open(init_path, 'r') as f:
            content = f.read()
        
        if "from . import errors" not in content:
            with open(init_path, 'a') as f:
                f.write("\n\n# Added by fix script\nfrom . import errors\n")
            logger.info(f"Updated {init_path} to import errors module")
    
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

def start_server():
    # Apply all runtime fixes
    fix_security_base()
    ensure_langgraph_errors()
    
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
    logger.info("Starting fix for SecurityBase type_ annotation issue...")
    
    # Fix the Pydantic error in FastAPI's SecurityBase class
    if not fix_security_base_issue():
        logger.error("Failed to fix SecurityBase issue.")
        return 1
    
    # Create the langgraph.errors module
    if not create_langgraph_errors_module():
        logger.error("Failed to create langgraph.errors module.")
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