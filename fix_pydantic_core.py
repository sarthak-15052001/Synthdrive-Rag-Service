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

def patch_pydantic_core_init():
    """
    Directly patch the pydantic_core/__init__.py file to fix the Sentinel issue.
    """
    logger.info("Patching pydantic_core/__init__.py")
    
    # Path to the pydantic_core/__init__.py file
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    pydantic_core_init_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic_core/__init__.py")
    
    if not os.path.exists(pydantic_core_init_path):
        logger.error(f"Could not find pydantic_core/__init__.py at {pydantic_core_init_path}")
        return False
    
    # Read the file
    with open(pydantic_core_init_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic line
    if "MISSING = Sentinel('MISSING')" in content:
        logger.info("Found problematic line, replacing it")
        
        # First, replace the Sentinel import
        content = content.replace(
            "from typing_extensions import Sentinel",
            """# Define our own Sentinel class
class Sentinel:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Sentinel({self.name!r})"
"""
        )
        
        # Write the modified content back
        with open(pydantic_core_init_path, 'w') as f:
            f.write(content)
        
        logger.info("Successfully patched pydantic_core/__init__.py")
        return True
    else:
        logger.warning("Could not find problematic line in pydantic_core/__init__.py")
        return False

if __name__ == "__main__":
    logger.info("Starting patch script")
    
    # Apply patch
    if patch_pydantic_core_init():
        logger.info("Patch applied successfully")
        
        # Create a startup script
        startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_fixed_core.py")
        with open(startup_script_path, 'w') as f:
            f.write("""#!/usr/bin/env python3
import os
import sys
import logging
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

# Start the server
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
        logger.info("Run ./start_fixed_core.py to start the server with patches applied")
    else:
        logger.error("Failed to apply patch")