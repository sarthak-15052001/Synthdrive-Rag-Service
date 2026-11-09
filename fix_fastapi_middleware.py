#!/usr/bin/env python3
import subprocess
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the output."""
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
        return e.stderr

def main():
    """Fix FastAPI middleware compatibility issues."""
    logger.info("Starting fix for FastAPI middleware compatibility issues...")
    
    # Get the virtual environment Python path
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        logger.error(f"Virtual environment Python not found at {venv_python}")
        venv_python = sys.executable
        logger.info(f"Using system Python instead: {venv_python}")
    
    # Step 1: Check current FastAPI version
    current_fastapi = run_command(f"{venv_python} -m pip show fastapi")
    logger.info(f"Current FastAPI installation:\n{current_fastapi}")
    
    # Step 2: Install a compatible version of FastAPI
    logger.info("Installing compatible version of FastAPI...")
    run_command(f"{venv_python} -m pip install fastapi==0.95.2 starlette==0.27.0")
    
    # Step 3: Verify installation
    new_fastapi = run_command(f"{venv_python} -m pip show fastapi")
    logger.info(f"New FastAPI installation:\n{new_fastapi}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()