#!/usr/bin/env python3
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_pydantic_module_path(module_name):
    """Find the path to a pydantic module in the virtual environment"""
    logger.info(f"Finding pydantic.{module_name} module path...")
    
    # Get the virtual environment path
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    # Search for pydantic directory
    for root, dirs, files in os.walk(venv_path):
        if "pydantic" in dirs:
            pydantic_dir = os.path.join(root, "pydantic")
            module_path = os.path.join(pydantic_dir, f"{module_name}.py")
            if os.path.exists(module_path):
                logger.info(f"Found pydantic.{module_name} at: {module_path}")
                return module_path
    
    logger.error(f"Could not find pydantic.{module_name} module")
    return None

def add_model_field_to_pydantic():
    """Add ModelField class directly to pydantic/fields.py"""
    fields_path = find_pydantic_module_path("fields")
    if not fields_path:
        return False
    
    # Create a backup of the original file
    backup_path = fields_path + ".bak"
    if not os.path.exists(backup_path):
        logger.info(f"Creating backup at {backup_path}")
        with open(fields_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    # Read the file content
    with open(fields_path, 'r') as f:
        content = f.read()
    
    # Check if ModelField already exists
    if "class ModelField" in content:
        logger.info("ModelField class already exists in pydantic.fields")
        return True
    
    # Add ModelField class to the end of the file
    model_field_code = """
# Added ModelField class for FastAPI compatibility
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
        return self.default
"""
    
    # Write the modified content back to the file
    with open(fields_path, 'w') as f:
        f.write(content + model_field_code)
    
    logger.info("Successfully added ModelField class to pydantic.fields")
    return True

def add_undefined_to_pydantic():
    """Add Undefined symbol and UndefinedType to pydantic/fields.py"""
    fields_path = find_pydantic_module_path("fields")
    if not fields_path:
        return False
    
    # Read the file content
    with open(fields_path, 'r') as f:
        content = f.read()
    
    # Check if Undefined and UndefinedType already exist
    if ("class UndefinedType" in content or "UndefinedType = " in content) and \
       ("class Undefined" in content or "Undefined = " in content):
        logger.info("Undefined and UndefinedType symbols already exist in pydantic.fields")
        return True
    
    # Add Undefined class and UndefinedType to the end of the file
    # We need to make sure these are directly accessible in the module namespace
    undefined_code = """
# Added Undefined class and UndefinedType for FastAPI compatibility
class UndefinedType:
    def __repr__(self):
        return "Undefined"
    
    def __bool__(self):
        return False

# Create a singleton instance
Undefined = UndefinedType()

# Make sure these are directly accessible in the module namespace
import sys
current_module = sys.modules[__name__]
setattr(current_module, 'UndefinedType', UndefinedType)
setattr(current_module, 'Undefined', Undefined)

# Also update __all__ if it exists
if hasattr(current_module, '__all__'):
    if 'UndefinedType' not in current_module.__all__:
        current_module.__all__.append('UndefinedType')
    if 'Undefined' not in current_module.__all__:
        current_module.__all__.append('Undefined')
else:
    current_module.__all__ = ['UndefinedType', 'Undefined']
"""
    
    # Write the modified content back to the file
    with open(fields_path, 'w') as f:
        f.write(content + undefined_code)
    
    logger.info("Successfully added Undefined symbol to pydantic.fields")
    return True

def add_validator_to_pydantic():
    """Add Validator class to pydantic/class_validators.py"""
    validators_path = find_pydantic_module_path("class_validators")
    if not validators_path:
        return False
    
    # Create a backup of the original file
    backup_path = validators_path + ".bak"
    if not os.path.exists(backup_path):
        logger.info(f"Creating backup at {backup_path}")
        with open(validators_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    # Read the file content
    with open(validators_path, 'r') as f:
        content = f.read()
    
    # Check if Validator already exists
    if "class Validator" in content:
        logger.info("Validator class already exists in pydantic.class_validators")
        return True
    
    # Add Validator class to the end of the file
    validator_code = """
# Added Validator class for FastAPI compatibility
class Validator:
    def __init__(self, func, pre=False, each_item=False, always=False, check_fields=True, **kwargs):
        self.func = func
        self.pre = pre
        self.each_item = each_item
        self.always = always
        self.check_fields = check_fields
        self.kwargs = kwargs
        
    def __repr__(self):
        return f"Validator(func={self.func.__name__})"
"""
    
    # Write the modified content back to the file
    with open(validators_path, 'w') as f:
        f.write(content + validator_code)
    
    logger.info("Successfully added Validator class to pydantic.class_validators")
    return True

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
    logger.info("Starting direct fixes for pydantic and FastAPI compatibility...")
    
    # Add ModelField to pydantic.fields
    add_model_field_to_pydantic()
    
    # Add Undefined to pydantic.fields
    add_undefined_to_pydantic()
    
    # Add Validator to pydantic.class_validators
    add_validator_to_pydantic()
    
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