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

def fix_fields_file():
    """
    Fix the incomplete import in _fields.py
    """
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    fields_path = os.path.join(venv_path, "lib/python3.12/site-packages/pydantic/_internal/_fields.py")
    
    if not os.path.exists(fields_path):
        logger.error(f"Could not find _fields.py at {fields_path}")
        return False
    
    logger.info(f"Reading {fields_path}")
    with open(fields_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = fields_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup at {backup_path}")
    
    # Fix the incomplete import
    modified_content = content.replace(
        "from typing_extensions import \nimport typing",
        "import typing"
    )
    
    # Write the modified content back
    with open(fields_path, 'w') as f:
        f.write(modified_content)
    
    logger.info(f"Fixed incomplete import in {fields_path}")
    return True

def create_startup_script():
    """
    Create a startup script that applies all necessary patches.
    """
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_with_all_fixes.py")
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

# Apply TypeIs fix
logger.info("Applying TypeIs fix")
import typing
if not hasattr(typing, 'TypeIs'):
    # Add TypeIs to typing module
    typing.TypeIs = typing.Type
    logger.info("Added TypeIs to typing module")

# Start the server
logger.info("Starting server with all fixes applied")
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
    logger.info("Starting fix script for _fields.py")
    
    # Fix _fields.py
    if fix_fields_file():
        logger.info("Successfully fixed _fields.py")
    else:
        logger.error("Failed to fix _fields.py")
        sys.exit(1)
    
    # Create startup script
    if create_startup_script():
        logger.info("Successfully created startup script")
    else:
        logger.error("Failed to create startup script")
        sys.exit(1)
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_with_all_fixes.py to start the server with all patches applied")