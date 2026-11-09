#!/usr/bin/env python3
import os
import sys
import logging
import types
from typing import ForwardRef, Any, Dict, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_forwardref():
    """
    Monkey patch the ForwardRef._evaluate method to handle the recursive_guard parameter
    that was added in Python 3.12 but not supported in older pydantic versions.
    """
    logger.info("Applying ForwardRef._evaluate patch for Python 3.12 compatibility")
    
    # Store the original _evaluate method
    original_evaluate = ForwardRef._evaluate
    
    # Define the patched method
    def patched_evaluate(self, globalns: Dict[str, Any], localns: Optional[Dict[str, Any]], 
                         recursive_guard: Optional[Set[Any]] = None) -> Any:
        """
        Patched version of ForwardRef._evaluate that handles the recursive_guard parameter
        added in Python 3.12.
        """
        # If recursive_guard is provided (Python 3.12+), but the original method doesn't accept it
        if recursive_guard is not None:
            # Call the original method without the recursive_guard parameter
            return original_evaluate(self, globalns, localns)
        else:
            # Call the original method as is
            return original_evaluate(self, globalns, localns)
    
    # Apply the patch
    ForwardRef._evaluate = patched_evaluate
    logger.info("ForwardRef._evaluate successfully patched")

def patch_typing_extensions():
    """
    Add the Sentinel symbol to typing_extensions if it's missing.
    """
    try:
        import typing_extensions
        if not hasattr(typing_extensions, 'Sentinel'):
            logger.info("Adding Sentinel to typing_extensions")
            # Create a simple Sentinel class similar to what typing_extensions would have
            class _SentinelType:
                def __repr__(self):
                    return "Sentinel"
            
            typing_extensions.Sentinel = _SentinelType()
            logger.info("Successfully added Sentinel to typing_extensions")
    except ImportError:
        logger.warning("typing_extensions module not found, skipping Sentinel patch")

if __name__ == "__main__":
    logger.info("Starting ForwardRef patch script")
    
    # Apply patches
    patch_forwardref()
    patch_typing_extensions()
    
    logger.info("Patches applied successfully")
    
    # Start the server
    port = 8000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    
    logger.info(f"Starting server on port {port}...")
    
    # Import the patched modules
    import uvicorn
    
    # Run the server
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(port), reload=True)