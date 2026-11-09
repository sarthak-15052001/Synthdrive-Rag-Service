#!/usr/bin/env python3
import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def apply_sentinel_fix():
    # Fix for Sentinel issue in pydantic_core
    import pydantic_core
    
    class Sentinel:
        def __init__(self, name):
            self.name = name
        
        def __repr__(self):
            return f'<{self.name}>'
    
    # Apply the fix
    pydantic_core.Sentinel = Sentinel
    pydantic_core.MISSING = Sentinel('MISSING')
    logger.info("Applied Sentinel fix")

def apply_typeis_fix():
    # Fix for TypeIs in typing_extensions
    import typing_extensions
    
    # Add TypeIs as an alias for Type if it doesn't exist
    if not hasattr(typing_extensions, 'TypeIs'):
        typing_extensions.TypeIs = typing_extensions.Type
        logger.info("Added TypeIs to typing_extensions")

def start_server():
    # Apply all fixes
    apply_sentinel_fix()
    apply_typeis_fix()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
