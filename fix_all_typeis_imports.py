#!/usr/bin/env python3
import os
import sys
import logging
import re
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_typeis_imports(file_path):
    """
    Fix TypeIs imports in a file by replacing them with typing.Type
    """
    if not os.path.exists(file_path):
        logger.error(f"Could not find file at {file_path}")
        return False
    
    logger.info(f"Reading {file_path}")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Create a backup
    backup_path = file_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup at {backup_path}")
    
    # Fix the import line
    modified_content = content
    
    # First, check if there's already a typing import
    has_typing_import = re.search(r'import\s+typing\b', content) is not None
    
    # Replace the TypeIs import
    if 'from typing_extensions import TypeIs' in content:
        # Simple case: only TypeIs is imported
        modified_content = modified_content.replace(
            'from typing_extensions import TypeIs',
            'import typing'
        )
    else:
        # Complex case: TypeIs is imported with other things
        modified_content = re.sub(
            r'from typing_extensions import (.*?)TypeIs(.*?)',
            lambda m: f'from typing_extensions import {m.group(1)}{m.group(2)}' +
                     ('' if has_typing_import else '\nimport typing'),
            modified_content
        )
    
    # If we don't have a typing import yet, add it
    if not has_typing_import and 'import typing' not in modified_content:
        modified_content = 'import typing\n' + modified_content
    
    # Also fix any usage of TypeIs in the file
    modified_content = re.sub(
        r'TypeIs\b',
        'typing.Type',  # Replace with standard typing.Type
        modified_content
    )
    
    # Write the modified content back
    with open(file_path, 'w') as f:
        f.write(modified_content)
    
    logger.info(f"Modified {file_path}")
    return True

def find_and_fix_all_typeis_imports():
    """
    Find all files with TypeIs imports and fix them
    """
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    site_packages = os.path.join(venv_path, "lib/python3.12/site-packages")
    
    # Find all Python files in site-packages
    python_files = glob.glob(f"{site_packages}/**/*.py", recursive=True)
    
    fixed_files = []
    for file_path in python_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file contains TypeIs import
        if 'TypeIs' in content:
            logger.info(f"Found TypeIs in {file_path}")
            if fix_typeis_imports(file_path):
                fixed_files.append(file_path)
    
    return fixed_files

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
    logger.info("Starting fix script for all TypeIs imports")
    
    # Fix all TypeIs imports
    fixed_files = find_and_fix_all_typeis_imports()
    if fixed_files:
        logger.info(f"Successfully fixed TypeIs imports in {len(fixed_files)} files")
        for file in fixed_files:
            logger.info(f"  - {file}")
    else:
        logger.error("Failed to fix any TypeIs imports")
        sys.exit(1)
    
    # Create startup script
    if create_startup_script():
        logger.info("Successfully created startup script")
    else:
        logger.error("Failed to create startup script")
        sys.exit(1)
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_with_all_fixes.py to start the server with all patches applied")