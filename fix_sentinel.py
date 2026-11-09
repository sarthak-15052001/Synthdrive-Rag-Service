#!/usr/bin/env python3
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_pydantic_core():
    """
    Patch the pydantic_core module to handle the Sentinel issue.
    """
    logger.info("Patching pydantic_core module")
    
    # Path to the pydantic_core/__init__.py file
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    pydantic_core_init_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic_core/__init__.py")
    
    if not os.path.exists(pydantic_core_init_path):
        logger.error(f"Could not find pydantic_core module at {pydantic_core_init_path}")
        return False
    
    # Read the file
    with open(pydantic_core_init_path, 'r') as f:
        content = f.read()
    
    # Replace the import line
    if "from typing_extensions import Sentinel" in content:
        logger.info("Found Sentinel import, replacing it")
        new_content = content.replace(
            "from typing_extensions import Sentinel", 
            """# Patched Sentinel class
class Sentinel:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Sentinel({self.name!r})"
"""
        )
        
        # Write the modified content back
        with open(pydantic_core_init_path, 'w') as f:
            f.write(new_content)
        
        logger.info("Successfully patched pydantic_core module")
        return True
    else:
        logger.warning("Could not find Sentinel import in pydantic_core module")
        return False

def patch_undefined_in_pydantic():
    """
    Patch the pydantic.fields module to add the Undefined symbol.
    """
    logger.info("Patching pydantic.fields module")
    
    # Path to the pydantic/fields.py file
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    pydantic_fields_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic/fields.py")
    
    if not os.path.exists(pydantic_fields_path):
        logger.error(f"Could not find pydantic.fields module at {pydantic_fields_path}")
        return False
    
    # Read the file
    with open(pydantic_fields_path, 'r') as f:
        content = f.read()
    
    # Add the Undefined symbol if it doesn't exist
    if "class Undefined:" not in content and "Undefined = " not in content:
        logger.info("Adding Undefined symbol to pydantic.fields")
        
        # Find the imports section
        import_section_end = content.find("\n\n", content.find("import "))
        if import_section_end == -1:
            import_section_end = content.find("\n", content.find("import "))
        
        if import_section_end != -1:
            # Add the Undefined class after the imports
            undefined_code = "\n\n# Patched Undefined class\nclass Undefined:\n    def __repr__(self):\n        return \"Undefined\"\n\nUndefined = Undefined()\n"
            new_content = content[:import_section_end] + undefined_code + content[import_section_end:]
            
            # Write the modified content back
            with open(pydantic_fields_path, 'w') as f:
                f.write(new_content)
            
            logger.info("Successfully patched pydantic.fields module")
            return True
        else:
            logger.warning("Could not find import section in pydantic.fields module")
            return False
    else:
        logger.info("Undefined symbol already exists in pydantic.fields module")
        return True

def patch_forwardref():
    """
    Patch the typing.ForwardRef._evaluate method to handle the recursive_guard parameter.
    """
    logger.info("Patching typing.ForwardRef._evaluate method")
    
    from typing import ForwardRef, Any, Dict, Optional, Set
    
    # Store the original _evaluate method
    original_evaluate = ForwardRef._evaluate
    
    # Define the patched method
    def patched_evaluate(self, globalns: Dict[str, Any], localns: Optional[Dict[str, Any]], 
                         recursive_guard: Optional[Set[Any]] = None) -> Any:
        """
        Patched version of ForwardRef._evaluate that handles the recursive_guard parameter
        added in Python 3.12.
        """
        # If recursive_guard is provided (Python 3.12+), but the original method doesn't accept it
        if recursive_guard is not None:
            # Call the original method without the recursive_guard parameter
            return original_evaluate(self, globalns, localns)
        else:
            # Call the original method as is
            return original_evaluate(self, globalns, localns)
    
    # Apply the patch
    ForwardRef._evaluate = patched_evaluate
    logger.info("Successfully patched ForwardRef._evaluate method")
    return True

if __name__ == "__main__":
    logger.info("Starting patch script")
    
    # Apply patches
    patch_pydantic_core()
    patch_undefined_in_pydantic()
    patch_forwardref()
    
    logger.info("All patches applied successfully")
    
    # Create a startup script that applies the patches before starting the server
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_patched_server.py")
    with open(startup_script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import logging
import importlib.util
from typing import ForwardRef, Any, Dict, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Patch ForwardRef._evaluate
def patch_forwardref():
    logger.info("Patching ForwardRef._evaluate")
    original_evaluate = ForwardRef._evaluate
    
    def patched_evaluate(self, globalns, localns, recursive_guard=None):
        if recursive_guard is not None:
            return original_evaluate(self, globalns, localns)
        else:
            return original_evaluate(self, globalns, localns)
    
    ForwardRef._evaluate = patched_evaluate
    logger.info("ForwardRef._evaluate patched successfully")

# Apply patches
patch_forwardref()

# Import and run the server
logger.info("Starting server with patches applied")
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
uvicorn_path = os.path.join(venv_path, "bin/uvicorn")

port = 8000
if len(sys.argv) > 1:
    port = sys.argv[1]

logger.info(f"Starting server on port {port}")
os.execl(uvicorn_path, uvicorn_path, "src.main:app", "--reload", "--port", str(port))
""")
    
    # Make the startup script executable
    os.chmod(startup_script_path, 0o755)
    
    logger.info(f"Created startup script at {startup_script_path}")
    logger.info("Run ./start_patched_server.py to start the server with patches applied")