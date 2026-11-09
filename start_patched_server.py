#!/usr/bin/env python3
import os
import sys
import logging
import importlib.util
from typing import ForwardRef, Any, Dict, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Patch ForwardRef._evaluate
def patch_forwardref():
    logger.info("Patching ForwardRef._evaluate")
    original_evaluate = ForwardRef._evaluate
    
    def patched_evaluate(self, globalns, localns, recursive_guard=None):
        if recursive_guard is not None:
            return original_evaluate(self, globalns, localns)
        else:
            return original_evaluate(self, globalns, localns)
    
    ForwardRef._evaluate = patched_evaluate
    logger.info("ForwardRef._evaluate patched successfully")

# Apply patches
patch_forwardref()

# Import and run the server
logger.info("Starting server with patches applied")
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
uvicorn_path = os.path.join(venv_path, "bin/uvicorn")

port = 8000
if len(sys.argv) > 1:
    port = sys.argv[1]

logger.info(f"Starting server on port {port}")
os.execl(uvicorn_path, uvicorn_path, "src.main:app", "--reload", "--port", str(port))
