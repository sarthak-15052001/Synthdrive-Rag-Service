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

def fix_pydantic_core_sentinel():
    """
    Directly modify the pydantic_core/__init__.py file to fix the Sentinel issue.
    This is a more targeted fix specifically for the Sentinel error.
    """
    # First, find the pydantic_core package in the virtual environment
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    pydantic_core_init_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic_core/__init__.py")
    
    if not os.path.exists(pydantic_core_init_path):
        logger.error(f"Could not find pydantic_core/__init__.py at {pydantic_core_init_path}")
        return False
    
    logger.info(f"Reading {pydantic_core_init_path}")
    with open(pydantic_core_init_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = pydantic_core_init_path + '.bak2'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup at {backup_path}")
    
    # Find the problematic line with Sentinel
    sentinel_line_pattern = r'MISSING = Sentinel\(\'MISSING\'\)'
    
    if re.search(sentinel_line_pattern, content):
        # Replace the problematic line with a direct assignment
        modified_content = re.sub(
            sentinel_line_pattern,
            "# Custom fix for Sentinel issue\nclass _CustomSentinel:\n    def __init__(self, name):\n        self.name = name\n    \n    def __repr__(self):\n        return f\"Sentinel({self.name!r})\"\n\nMISSING = _CustomSentinel('MISSING')",
            content
        )
        
        # Write the modified content back
        with open(pydantic_core_init_path, 'w') as f:
            f.write(modified_content)
        
        logger.info(f"Modified {pydantic_core_init_path} to fix Sentinel issue")
        return True
    else:
        logger.error(f"Could not find the Sentinel line in {pydantic_core_init_path}")
        return False

def create_startup_script():
    """
    Create a startup script that applies the fix and starts the server.
    """
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_fixed_server.py")
    with open(startup_script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Start the server
logger.info("Starting server with fixed pydantic_core")
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
    logger.info("Starting fix script for Sentinel error")
    
    # Fix pydantic_core Sentinel issue
    if fix_pydantic_core_sentinel():
        logger.info("Successfully fixed pydantic_core Sentinel issue")
    else:
        logger.error("Failed to fix pydantic_core Sentinel issue")
        sys.exit(1)
    
    # Create startup script
    if create_startup_script():
        logger.info("Successfully created startup script")
    else:
        logger.error("Failed to create startup script")
        sys.exit(1)
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_fixed_server.py to start the server with the fix applied")