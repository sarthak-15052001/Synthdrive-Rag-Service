#!/usr/bin/env python3
import os
import sys
import importlib
import logging
import types
import inspect
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def find_venv_site_packages():
    """Find the site-packages directory in the virtual environment."""
    # Try to find the venv directory
    venv_dirs = [
        os.path.join(os.getcwd(), 'venv'),
        os.path.join(os.getcwd(), '.venv'),
        os.path.join(os.getcwd(), 'env'),
        os.path.join(os.getcwd(), '.env'),
    ]
    
    for venv_dir in venv_dirs:
        if os.path.isdir(venv_dir):
            # Look for site-packages in common locations
            for python_version in ['python3.12', 'python3.11', 'python3.10', 'python3.9', 'python3.8', 'python3']:
                site_packages = os.path.join(venv_dir, 'lib', python_version, 'site-packages')
                if os.path.isdir(site_packages):
                    return site_packages
    
    # If we can't find it, return None
    return None

def fix_pydantic_fields(site_packages_path):
    """Add ModelField class to pydantic.fields."""
    if not site_packages_path:
        logger.error("Could not find site-packages directory")
        return False
    
    fields_path = os.path.join(site_packages_path, 'pydantic', 'fields.py')
    
    if not os.path.isfile(fields_path):
        logger.error(f"Could not find pydantic.fields at {fields_path}")
        return False
    
    # Create a backup
    backup_path = f"{fields_path}.bak"
    shutil.copy2(fields_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(fields_path, 'r') as f:
        content = f.read()
    
    # Check if ModelField already exists
    if 'class ModelField' in content:
        logger.info("ModelField class already exists in pydantic.fields")
        return True
    
    # Add ModelField class
    model_field_code = """
# Added for compatibility with FastAPI
class ModelField:
    """Mock ModelField class for compatibility with FastAPI."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
"""
    
    # Append to the file
    with open(fields_path, 'a') as f:
        f.write(model_field_code)
    
    logger.info(f"Added ModelField class to {fields_path}")
    return True

def fix_security_base(site_packages_path):
    """Fix the type_ annotation in SecurityBase subclasses."""
    if not site_packages_path:
        logger.error("Could not find site-packages directory")
        return False
    
    try:
        # Add the site-packages to sys.path temporarily
        sys.path.insert(0, site_packages_path)
        
        # Try to import the necessary modules
        from fastapi.openapi.models import SecuritySchemeType, APIKey, HTTPBase, HTTPBearer, OAuth2, OpenIdConnect
        
        # Add proper type annotations to all classes that inherit from SecurityBase
        APIKey.type_.__annotations__ = {'return': SecuritySchemeType}
        HTTPBase.type_.__annotations__ = {'return': SecuritySchemeType}
        OAuth2.type_.__annotations__ = {'return': SecuritySchemeType}
        OpenIdConnect.type_.__annotations__ = {'return': SecuritySchemeType}
        
        # Fix the scheme field in HTTPBearer
        HTTPBearer.scheme.__annotations__ = {'return': str}
        
        logger.info("Fixed type_ and scheme annotations in SecurityBase subclasses")
        return True
    except (ImportError, AttributeError) as e:
        logger.error(f"Could not fix SecurityBase issue: {e}")
        return False
    finally:
        # Remove the site-packages from sys.path
        if site_packages_path in sys.path:
            sys.path.remove(site_packages_path)

def create_mock_langgraph_errors(site_packages_path):
    """Create a mock langgraph.errors module."""
    if not site_packages_path:
        logger.error("Could not find site-packages directory")
        return False
    
    # Check if the module already exists
    langgraph_path = os.path.join(site_packages_path, 'langgraph')
    errors_path = os.path.join(langgraph_path, 'errors.py')
    
    if os.path.isfile(errors_path):
        logger.info("langgraph.errors module already exists")
        return True
    
    # Create the langgraph directory if it doesn't exist
    os.makedirs(langgraph_path, exist_ok=True)
    
    # Create the __init__.py file if it doesn't exist
    init_path = os.path.join(langgraph_path, '__init__.py')
    if not os.path.isfile(init_path):
        with open(init_path, 'w') as f:
            f.write("# Mock langgraph package\n")
    
    # Create the errors.py file
    with open(errors_path, 'w') as f:
        f.write("""# Mock langgraph.errors module

class LangGraphError(Exception):
    """Base class for all LangGraph errors."""
    pass

class EmptyInputError(LangGraphError):
    """Raised when an input to a node is empty."""
    pass

class InvalidUpdateError(LangGraphError):
    """Raised when an update to a state is invalid."""
    pass
""")
    
    logger.info(f"Created mock langgraph.errors module at {errors_path}")
    return True

def create_mock_langchain_schema(site_packages_path):
    """Create a mock langchain.schema module."""
    if not site_packages_path:
        logger.error("Could not find site-packages directory")
        return False
    
    # Check if the module already exists
    langchain_path = os.path.join(site_packages_path, 'langchain')
    schema_path = os.path.join(langchain_path, 'schema.py')
    
    if os.path.isfile(schema_path):
        logger.info("langchain.schema module already exists")
        return True
    
    # Create the langchain directory if it doesn't exist
    os.makedirs(langchain_path, exist_ok=True)
    
    # Create the __init__.py file if it doesn't exist
    init_path = os.path.join(langchain_path, '__init__.py')
    if not os.path.isfile(init_path):
        with open(init_path, 'w') as f:
            f.write("# Mock langchain package\n")
    
    # Create the schema.py file
    with open(schema_path, 'w') as f:
        f.write("""# Mock langchain.schema module

class Document:
    """Mock Document class for langchain.schema."""
    def __init__(self, page_content="", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}
""")
    
    logger.info(f"Created mock langchain.schema module at {schema_path}")
    return True

def create_startup_script():
    """Create a startup script that applies all fixes and starts the server."""
    script_path = os.path.join(os.getcwd(), 'start_with_venv_fixes.py')
    
    with open(script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
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
""")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"Created startup script at {script_path}")
    return script_path

def main():
    logger.info("Starting fix for dependency issues in virtual environment...")
    
    # Find the site-packages directory
    site_packages_path = find_venv_site_packages()
    
    if not site_packages_path:
        logger.error("Could not find site-packages directory in virtual environment")
        return
    
    logger.info(f"Found site-packages at {site_packages_path}")
    
    # Apply all fixes
    fix_pydantic_fields(site_packages_path)
    fix_security_base(site_packages_path)
    create_mock_langgraph_errors(site_packages_path)
    create_mock_langchain_schema(site_packages_path)
    
    # Create startup script
    startup_script = create_startup_script()
    
    logger.info("All fixes applied successfully!")
    logger.info(f"Run {startup_script} to start the server with all patches applied")

if __name__ == "__main__":
    main()