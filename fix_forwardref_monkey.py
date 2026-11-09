#!/usr/bin/env python3
"""
This script creates a monkey patch for the ForwardRef._evaluate method in typing.py.
It directly modifies the ForwardRef class to handle the recursive_guard parameter.
"""

import os
import sys
import logging
from typing import ForwardRef, Any, Dict, Optional, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Store the original _evaluate method
original_evaluate = ForwardRef._evaluate

# Define a new _evaluate method that handles the recursive_guard parameter
def patched_evaluate(self, globalns, localns, recursive_guard=None):
    """
    Patched version of ForwardRef._evaluate that handles the recursive_guard parameter.
    This is needed because Python 3.12 requires this parameter, but older versions of pydantic
    don't pass it.
    """
    logger.info("Using patched ForwardRef._evaluate method")
    # Just pass the first two arguments to the original method
    return original_evaluate(self, globalns, localns)

# Apply the patch
ForwardRef._evaluate = patched_evaluate

logger.info("ForwardRef._evaluate patched successfully")

# Create a startup script
startup_script = """#!/usr/bin/env python3
import os
import sys
import subprocess

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the monkey patch before anything else
import fix_forwardref_monkey

# Start the server
port = 8000
if len(sys.argv) > 1:
    port = sys.argv[1]

print(f"Starting server on port {port}...")
# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/uvicorn"),
    "src.main:app",
    "--reload",
    "--port", str(port)
])
"""

with open("start_with_monkey_patch.py", 'w') as f:
    f.write(startup_script)

# Make the startup script executable
os.chmod("start_with_monkey_patch.py", 0o755)

logger.info("Created start_with_monkey_patch.py")
logger.info("Please run ./start_with_monkey_patch.py to start the server with the monkey patch applied")