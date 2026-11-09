"""
Script to update the API endpoint to use the improved Kernel of Truth implementation.
This script creates a symbolic link to the improved implementation.
"""

import os
import logging
import shutil
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_api_endpoint():
    """
    Update the API endpoint to use the improved Kernel of Truth implementation.
    """
    try:
        # Paths to the original and improved implementations
        original_path = "src/querying/tools/kernel_of_truth.py"
        improved_path = "src/querying/tools/kernel_of_truth_improved.py"
        backup_path = "src/querying/tools/kernel_of_truth.py.bak"
        
        # Check if the files exist
        if not os.path.exists(original_path):
            logger.error(f"Original file not found: {original_path}")
            return False
        
        if not os.path.exists(improved_path):
            logger.error(f"Improved file not found: {improved_path}")
            return False
        
        # Create a backup of the original file
        logger.info(f"Creating backup of original file: {backup_path}")
        shutil.copy2(original_path, backup_path)
        
        # Replace the original file with the improved implementation
        logger.info(f"Replacing {original_path} with {improved_path}")
        shutil.copy2(improved_path, original_path)
        
        logger.info("API endpoint updated to use improved Kernel of Truth implementation")
        return True
    
    except Exception as e:
        logger.error(f"Error updating API endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_api_endpoint()
    sys.exit(0 if success else 1)