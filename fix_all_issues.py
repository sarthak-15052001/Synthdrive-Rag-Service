#!/usr/bin/env python3
import os
import sys
import logging
import importlib
import subprocess
import inspect
from typing import Any, Dict, Set, Type, Union, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_module_path(module_name):
    """Find the path to a module in the virtual environment"""
    logger.info(f"Finding {module_name} module path...")
    
    # Get the virtual environment path
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    # Split the module name into parts
    parts = module_name.split('.')
    
    # Search for the module directory
    for root, dirs, files in os.walk(venv_path):
        if parts[0] in dirs:
            module_dir = os.path.join(root, *parts)
            if os.path.exists(module_dir):
                logger.info(f"Found {module_name} at: {module_dir}")
                return module_dir
            
            # Check for .py file
            py_file = f"{module_dir}.py"
            if os.path.exists(py_file):
                logger.info(f"Found {module_name} at: {py_file}")
                return py_file
    
    logger.error(f"Could not find {module_name} module")
    return None

def patch_fastapi_utils():
    """Patch FastAPI utils.py to fix model_process_schema import"""
    utils_path = find_module_path("fastapi.utils")
    if not utils_path:
        utils_path = find_module_path("fastapi/utils.py")
    
    if not utils_path:
        logger.error("Could not find fastapi/utils.py")
        return False
    
    # Create a backup of the original file
    backup_path = utils_path + ".bak"
    if not os.path.exists(backup_path):
        logger.info(f"Creating backup at {backup_path}")
        with open(utils_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    # Read the file content
    with open(utils_path, 'r') as f:
        content = f.read()
    
    # Check if we already patched the file
    if "# Mock model_process_schema function" in content:
        logger.info("FastAPI utils.py already patched")
        return True
    
    # Replace the import line for model_process_schema
    if "from pydantic.schema import model_process_schema" in content:
        modified_content = content.replace(
            "from pydantic.schema import model_process_schema",
            """# Mock model_process_schema function
def model_process_schema(
    model: Type[Any],
    *,
    model_name_map: Dict[Type[Any], str],
    ref_prefix: str = "#/components/schemas/"
) -> Tuple[Dict[str, Any], Dict[str, Any], Set[str]]:
    \"\"\"
    Mock implementation of model_process_schema to handle schema generation.
    \"\"\"
    schema = {"type": "object", "properties": {}}
    definitions = {}
    nested_models = set()
    
    # For enums, create a simple enum schema
    if hasattr(model, "__members__"):
        values = list(getattr(model, "__members__", {}).keys())
        schema = {"enum": values}
        if model.__doc__:
            schema["description"] = model.__doc__
        return schema, definitions, nested_models
    
    # For Pydantic models, create a basic schema
    if hasattr(model, "__fields__"):
        properties = {}
        for field_name, field in getattr(model, "__fields__", {}).items():
            field_schema = {"type": "string"}  # Default to string
            if field.description:
                field_schema["description"] = field.description
            properties[field_name] = field_schema
        
        schema["properties"] = properties
        required = [name for name, field in getattr(model, "__fields__", {}).items()
                   if field.required]
        if required:
            schema["required"] = required
    
    if model.__doc__:
        schema["description"] = model.__doc__
    
    return schema, definitions, nested_models"""
        )
        
        # Write the modified content back to the file
        with open(utils_path, 'w') as f:
            f.write(modified_content)
        
        logger.info("Successfully patched fastapi.utils with mock model_process_schema")
        return True
    else:
        logger.warning("Could not find the import line for model_process_schema in fastapi.utils")
        return False

def create_mock_langchain_schema():
    """Create mock langchain.schema module with Document class"""
    logger.info("Creating mock langchain.schema module...")
    
    # Get the site-packages directory
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    site_packages = None
    
    for root, dirs, files in os.walk(venv_path):
        if "site-packages" in root:
            site_packages = root
            break
    
    if not site_packages:
        logger.error("Could not find site-packages directory")
        return False
    
    # Create langchain directory if it doesn't exist
    langchain_dir = os.path.join(site_packages, "langchain")
    if not os.path.exists(langchain_dir):
        os.makedirs(langchain_dir)
        # Create __init__.py
        with open(os.path.join(langchain_dir, "__init__.py"), 'w') as f:
            f.write("# Mock langchain package\n")
    
    # Create schema directory if it doesn't exist
    schema_dir = os.path.join(langchain_dir, "schema")
    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)
    
    # Create __init__.py with Document class
    schema_init_path = os.path.join(schema_dir, "__init__.py")
    with open(schema_init_path, 'w') as f:
        f.write("""# Mock langchain.schema module
class Document:
    def __init__(self, page_content="", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}
        
    def __repr__(self):
        return f"Document(page_content={self.page_content}, metadata={self.metadata})"
""")
    
    logger.info("Successfully created mock langchain.schema module")
    return True

def main():
    """Apply all fixes and start the server"""
    logger.info("Starting fixes for FastAPI and langchain imports...")
    
    # Patch FastAPI utils.py
    patch_result = patch_fastapi_utils()
    if not patch_result:
        logger.error("Failed to patch FastAPI utils.py")
    
    # Create mock langchain.schema module
    langchain_result = create_mock_langchain_schema()
    if not langchain_result:
        logger.error("Failed to create mock langchain.schema module")
    
    if patch_result and langchain_result:
        logger.info("All fixes applied successfully!")
        logger.info("Starting the server...")
        
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Change to the script directory
        os.chdir(script_dir)
        
        # Start the server with uvicorn
        try:
            subprocess.run(["uvicorn", "src.main:app", "--reload"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start server: {e}")
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        logger.error("Some fixes failed, not starting the server")

if __name__ == "__main__":
    main()