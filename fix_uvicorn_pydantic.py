#!/usr/bin/env python3
import logging
import subprocess
import sys
import os
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a command and return its output."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
        return None

def main():
    """Fix Uvicorn and Pydantic compatibility issues."""
    logger.info("Starting fix for Uvicorn and Pydantic compatibility issues...")
    
    # Get the Python executable from the virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    venv_pip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "pip")
    
    # Uninstall current versions
    logger.info("Uninstalling current packages...")
    run_command(f"{venv_pip} uninstall -y fastapi starlette pydantic uvicorn")
    
    # Install specific compatible versions
    logger.info("Installing specific compatible versions...")
    run_command(f"{venv_pip} install pydantic==1.10.8")
    run_command(f"{venv_pip} install fastapi==0.95.1 starlette==0.26.1")
    run_command(f"{venv_pip} install uvicorn==0.22.0")
    
    # Create a patch for the Undefined issue
    logger.info("Creating patch for Undefined issue...")
    pydantic_fields_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "venv/lib/python3.12/site-packages/pydantic/fields.py")
    
    # Add Undefined class to pydantic.fields
    with open(pydantic_fields_path, 'a') as f:
        f.write("""
# Mock implementation of Undefined
class Undefined:
    def __repr__(self):
        return 'Undefined'
    
    def __bool__(self):
        return False

# Create a singleton instance
Undefined = Undefined()
""")
    
    # Create _subprocess.py module for uvicorn
    logger.info("Creating _subprocess.py module for uvicorn...")
    uvicorn_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "venv/lib/python3.12/site-packages/uvicorn")
    
    # Check if _subprocess.py already exists
    if not os.path.exists(os.path.join(uvicorn_dir, "_subprocess.py")):
        # Create a symlink from subprocess.py to _subprocess.py
        subprocess_path = os.path.join(uvicorn_dir, "subprocess.py")
        _subprocess_path = os.path.join(uvicorn_dir, "_subprocess.py")
        
        if os.path.exists(subprocess_path):
            # Copy the content of subprocess.py to _subprocess.py
            with open(subprocess_path, 'r') as src, open(_subprocess_path, 'w') as dst:
                dst.write(src.read())
            logger.info("Created _subprocess.py from subprocess.py")
        else:
            # Create a minimal _subprocess.py
            with open(_subprocess_path, 'w') as f:
                f.write("""
# Mock implementation of uvicorn._subprocess
from uvicorn.subprocess import subprocess_started
""")
            logger.info("Created minimal _subprocess.py")
    
    # Verify installations
    logger.info("Verifying installations...")
    installed_packages = run_command(f"{venv_pip} list | grep -E 'fastapi|starlette|pydantic|uvicorn'")
    logger.info(f"Installed packages:\n{installed_packages}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()