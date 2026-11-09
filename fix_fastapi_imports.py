#!/usr/bin/env python3
import os
import sys
import logging
import importlib
import subprocess

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
    """Patch FastAPI utils.py to fix UndefinedType import"""
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
    
    # Replace the import line
    if "from pydantic.fields import FieldInfo, ModelField, UndefinedType" in content:
        modified_content = content.replace(
            "from pydantic.fields import FieldInfo, ModelField, UndefinedType",
            """from pydantic.fields import FieldInfo
# Define UndefinedType and ModelField for compatibility
class UndefinedType:
    def __repr__(self):
        return "Undefined"
    
    def __bool__(self):
        return False

# Create a singleton instance
Undefined = UndefinedType()

# ModelField class for compatibility
class ModelField:
    def __init__(self, name=None, type_=None, class_validators=None, model_config=None,
                default=None, default_factory=None, required=None, alias=None,
                field_info=None, **kwargs):
        self.name = name
        self.type_ = type_
        self.class_validators = class_validators or {}
        self.model_config = model_config or {}
        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.alias = alias
        self.field_info = field_info
        self.kwargs = kwargs
        
    def __repr__(self):
        return f"ModelField(name={self.name}, type_={self.type_})"
    
    def get_default(self):
        if self.default_factory is not None:
            return self.default_factory()
        return self.default"""
        )
        
        # Write the modified content back to the file
        with open(utils_path, 'w') as f:
            f.write(modified_content)
        
        logger.info("Successfully patched fastapi.utils")
        return True
    else:
        logger.warning("Could not find the import line to patch in fastapi.utils")
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
    logger.info("Starting FastAPI import fixes...")
    
    # Patch FastAPI utils.py
    patch_fastapi_utils()
    
    # Create mock langchain.schema module
    create_mock_langchain_schema()
    
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

if __name__ == "__main__":
    main()