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

def fix_tuple_import():
    """Fix Tuple import in FastAPI utils.py"""
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
    
    # Fix Tuple reference
    if "Tuple[Dict[str, Any], Dict[str, Any], Set[str]]" in content:
        logger.info("Fixing Tuple reference in FastAPI utils.py")
        modified_content = content.replace(
            "Tuple[Dict[str, Any], Dict[str, Any], Set[str]]",
            "tuple[Dict[str, Any], Dict[str, Any], Set[str]]"
        )
        
        # Write the modified content back to the file
        with open(utils_path, 'w') as f:
            f.write(modified_content)
        
        logger.info("Successfully fixed Tuple reference in FastAPI utils.py")
        return True
    else:
        logger.warning("Could not find Tuple reference in FastAPI utils.py")
        return False

def main():
    """Fix Tuple import issue and start the server"""
    logger.info("Starting fix for Tuple import in FastAPI utils.py...")
    
    # Fix Tuple import
    fix_result = fix_tuple_import()
    if not fix_result:
        logger.error("Failed to fix Tuple import in FastAPI utils.py")
        return
    
    logger.info("Fix applied successfully!")
    logger.info("Starting the server...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Start the server with uvicorn
    try:
        import subprocess
        subprocess.run(["uvicorn", "src.main:app", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start server: {e}")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    main()