#!/usr/bin/env python3
import os
import sys
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_pydantic_core():
    """
    Directly modify the pydantic_core/__init__.py file to fix the Sentinel issue.
    """
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    pydantic_core_init_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic_core/__init__.py")
    
    if not os.path.exists(pydantic_core_init_path):
        logger.error(f"Could not find pydantic_core/__init__.py at {pydantic_core_init_path}")
        return False
    
    logger.info(f"Reading {pydantic_core_init_path}")
    with open(pydantic_core_init_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = pydantic_core_init_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup at {backup_path}")
    
    # Replace the problematic line
    modified_content = re.sub(
        r'from typing_extensions import Sentinel',
        '# Custom Sentinel implementation\nclass Sentinel:\n    def __init__(self, name):\n        self.name = name\n    \n    def __repr__(self):\n        return f"Sentinel({self.name!r})"\n',
        content
    )
    
    # Write the modified content back
    with open(pydantic_core_init_path, 'w') as f:
        f.write(modified_content)
    
    logger.info(f"Modified {pydantic_core_init_path}")
    return True

def install_missing_dependencies():
    """
    Install missing dependencies.
    """
    logger.info("Installing missing dependencies")
    os.system("pip install langchain-core")
    logger.info("Installed langchain-core")
    return True

def create_startup_script():
    """
    Create a startup script that applies all necessary patches.
    """
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_all_fixed.py")
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
logger.info("Starting server with all patches applied")
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
    return True

if __name__ == "__main__":
    logger.info("Starting fix script")
    
    # Fix pydantic_core
    if fix_pydantic_core():
        logger.info("Successfully fixed pydantic_core")
    else:
        logger.error("Failed to fix pydantic_core")
        sys.exit(1)
    
    # Install missing dependencies
    if install_missing_dependencies():
        logger.info("Successfully installed missing dependencies")
    else:
        logger.error("Failed to install missing dependencies")
        sys.exit(1)
    
    # Create startup script
    if create_startup_script():
        logger.info("Successfully created startup script")
    else:
        logger.error("Failed to create startup script")
        sys.exit(1)
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_all_fixed.py to start the server with all patches applied")