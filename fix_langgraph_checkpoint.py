#!/usr/bin/env python3
"""
Fix script for langgraph checkpoint compatibility issues.
This script installs the correct version of langgraph-checkpoint.
"""
import os
import sys
import subprocess
import logging

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
        "langgraph-checkpoint==3.0.1"  # Install the version that has CheckpointAt
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

def main():
    """Main function to fix langgraph checkpoint compatibility issues."""
    logger.info("Starting fix for langgraph checkpoint compatibility issues...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies. Exiting.")
        return 1
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")
    return 0

if __name__ == "__main__":
    sys.exit(main())