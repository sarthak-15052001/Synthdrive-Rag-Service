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

def add_typeis_to_typing_extensions():
    """
    Add TypeIs to typing_extensions.py directly
    """
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    typing_extensions_path = os.path.join(venv_path, "lib/python3.12/site-packages/typing_extensions.py")
    
    if not os.path.exists(typing_extensions_path):
        logger.error(f"Could not find typing_extensions.py at {typing_extensions_path}")
        return False
    
    logger.info(f"Reading {typing_extensions_path}")
    with open(typing_extensions_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = typing_extensions_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup at {backup_path}")
    
    # Check if TypeIs is already defined
    if "class TypeIs" in content:
        logger.info("TypeIs is already defined in typing_extensions.py")
        return True
    
    # Find a good place to add TypeIs - after the Type class
    if "class Type" in content:
        # Add TypeIs after Type
        modified_content = content.replace(
            "# End of Type class",
            """# End of Type class

# TypeIs is an alias for Type for compatibility
TypeIs = Type
"""
        )
        
        # If the marker isn't found, add it at the end
        if modified_content == content:
            logger.info("Adding TypeIs at the end of the file")
            modified_content = content + "\n\n# TypeIs is an alias for Type for compatibility\nTypeIs = Type\n"
    else:
        # If Type isn't found, add TypeIs at the end
        logger.info("Adding TypeIs at the end of the file")
        modified_content = content + "\n\n# TypeIs is an alias for Type for compatibility\nTypeIs = Type\n"
    
    # Write the modified content back
    with open(typing_extensions_path, 'w') as f:
        f.write(modified_content)
    
    logger.info(f"Added TypeIs to {typing_extensions_path}")
    return True

def create_startup_script():
    """
    Create a startup script that applies all necessary patches.
    """
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_with_typeis_fix.py")
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
logger.info("Starting server with TypeIs fix applied")
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
    logger.info("Starting fix script for TypeIs")
    
    # Add TypeIs to typing_extensions
    if add_typeis_to_typing_extensions():
        logger.info("Successfully added TypeIs to typing_extensions")
    else:
        logger.error("Failed to add TypeIs to typing_extensions")
        sys.exit(1)
    
    # Create startup script
    if create_startup_script():
        logger.info("Successfully created startup script")
    else:
        logger.error("Failed to create startup script")
        sys.exit(1)
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_with_typeis_fix.py to start the server with all patches applied")