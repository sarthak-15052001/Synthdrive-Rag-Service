#!/usr/bin/env python3
import logging
import subprocess
import sys
import os

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
    run_command(f"{venv_python} -m pip uninstall -y fastapi starlette pydantic pydantic-settings")
    
    # Install compatible versions
    # FastAPI 0.68.0 works with Pydantic 1.8.2
    run_command(f"{venv_python} -m pip install pydantic==1.8.2")
    run_command(f"{venv_python} -m pip install fastapi==0.68.0 starlette==0.14.2")
    
    # Verify installations
    logger.info("Verifying installations...")
    installed_packages = run_command(f"{venv_python} -m pip list | grep -E 'fastapi|starlette|pydantic'")
    logger.info(f"Installed packages:\n{installed_packages}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()