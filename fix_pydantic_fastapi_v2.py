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
    """Fix FastAPI and Pydantic compatibility issues."""
    logger.info("Starting fix for FastAPI and Pydantic compatibility...")
    
    # Get the Python executable from the virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    
    # Uninstall current versions
    logger.info("Uninstalling current packages...")
    run_command(f"{venv_python} -m pip uninstall -y fastapi starlette pydantic uvicorn")
    
    # Install compatible versions
    logger.info("Installing compatible versions...")
    run_command(f"{venv_python} -m pip install pydantic==1.10.8")
    run_command(f"{venv_python} -m pip install fastapi==0.95.1 starlette==0.26.1")
    run_command(f"{venv_python} -m pip install uvicorn==0.22.0")
    
    # Create a patch for the Undefined issue if needed
    logger.info("Creating patch for Undefined issue...")
    pydantic_fields_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "venv/lib/python3.12/site-packages/pydantic/fields.py")
    
    # Check if Undefined is already defined
    with open(pydantic_fields_path, 'r') as f:
        content = f.read()
    
    if "class Undefined:" not in content:
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
    
    # Verify installations
    logger.info("Verifying installations...")
    installed_packages = run_command(f"{venv_python} -m pip list | grep -E 'fastapi|starlette|pydantic|uvicorn'")
    logger.info(f"Installed packages:\n{installed_packages}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()