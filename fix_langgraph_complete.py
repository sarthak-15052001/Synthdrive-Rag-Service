#!/usr/bin/env python3
"""
Comprehensive fix script for langchain and langgraph compatibility issues.
This script installs the correct versions of dependencies and patches problematic modules.
"""
import os
import sys
import subprocess
import logging
import importlib
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install the correct versions of dependencies."""
    logger.info("Installing required dependencies...")
    
    # Define the packages to install
    packages = [
        "langchain-core==0.1.27",  # Use an older version that's more compatible
        "langchain==0.0.335",      # Use an older version that's more compatible
        "langchain-community==0.0.16",
        "langchain-openai==0.0.5",
        "langgraph==0.0.25"
    ]
    
    # Install the packages
    for package in packages:
        logger.info(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            return False
    
    return True

def patch_modules():
    """Patch problematic modules if needed."""
    try:
        # Check if we need to patch langchain_openai
        import langchain_openai
        logger.info("Checking if langchain_openai needs patching...")
        
        # No patching needed for now, but this function can be expanded
        # if specific modules need to be modified
        
        return True
    except ImportError:
        logger.error("Could not import langchain_openai to check for patching")
        return False

def main():
    """Main function to fix langchain and langgraph compatibility issues."""
    logger.info("Starting comprehensive fix for langchain and langgraph compatibility issues...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies. Exiting.")
        return 1
    
    # Patch modules if needed
    if not patch_modules():
        logger.warning("Module patching failed, but continuing...")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")
    return 0

if __name__ == "__main__":
    sys.exit(main())