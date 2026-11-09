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
    """Fix Pydantic and pydantic-settings compatibility issues."""
    logger.info("Starting fix for Pydantic and pydantic-settings compatibility issues...")
    
    # Get the virtual environment Python path
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        logger.error(f"Virtual environment Python not found at {venv_python}")
        venv_python = sys.executable
        logger.info(f"Using system Python instead: {venv_python}")
    
    # Step 1: Check current Pydantic version
    current_pydantic = run_command(f"{venv_python} -m pip show pydantic")
    logger.info(f"Current Pydantic installation:\n{current_pydantic}")
    
    # Step 2: Install compatible versions of Pydantic and pydantic-settings
    logger.info("Installing compatible versions of Pydantic and pydantic-settings...")
    run_command(f"{venv_python} -m pip install pydantic==1.10.8")
    run_command(f"{venv_python} -m pip install pydantic-settings==2.0.3")
    
    # Step 3: Verify installation
    new_pydantic = run_command(f"{venv_python} -m pip show pydantic")
    logger.info(f"New Pydantic installation:\n{new_pydantic}")
    
    new_pydantic_settings = run_command(f"{venv_python} -m pip show pydantic-settings")
    logger.info(f"New pydantic-settings installation:\n{new_pydantic_settings}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()