#!/usr/bin/env python3
import logging
import os
import sys
import inspect
from typing import ForwardRef

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Create a direct fix for the ForwardRef._evaluate issue."""
    logger.info("Starting direct fix for ForwardRef._evaluate issue...")
    
    # Check the current ForwardRef._evaluate method signature
    try:
        signature = inspect.signature(ForwardRef._evaluate)
        logger.info(f"Current ForwardRef._evaluate signature: {signature}")
        
        # Check if recursive_guard is a parameter
        has_recursive_guard = 'recursive_guard' in signature.parameters
        logger.info(f"Has recursive_guard parameter: {has_recursive_guard}")
        
        if not has_recursive_guard:
            # Create a monkey patch module
            logger.info("Creating monkey patch module...")
            with open("monkey_patch_typing.py", 'w') as f:
                f.write("""
# Monkey patch for typing.ForwardRef._evaluate
from typing import ForwardRef, Any, cast, get_type_hints
import sys
import types

# Store the original _evaluate method
original_evaluate = ForwardRef._evaluate

# Define a new _evaluate method that handles the recursive_guard parameter
def patched_evaluate(self, globalns, localns, recursive_guard=None):
    # Just pass the first two arguments to the original method
    return original_evaluate(self, globalns, localns)

# Apply the patch
ForwardRef._evaluate = patched_evaluate

print("ForwardRef._evaluate patched successfully")
""")
            
            # Create a startup script that applies the monkey patch
            logger.info("Creating startup script...")
            with open("start_with_patch.py", 'w') as f:
                f.write("""#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the monkey patch before importing anything else
print("Applying ForwardRef._evaluate patch...")
exec(open("monkey_patch_typing.py").read())

# Start the server
port = 8001
if len(sys.argv) > 1:
    port = sys.argv[1]

print(f"Starting server on port {port}...")
# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/python"),
    "-c",
    "import sys; sys.path.insert(0, '.'); import monkey_patch_typing; from uvicorn.main import main; sys.argv = ['uvicorn', 'src.main:app', '--reload', '--port', '" + str(port) + "']; main()",
])
""")
            
            # Make the startup script executable
            os.chmod("start_with_patch.py", 0o755)
            
            logger.info("Fix completed successfully!")
            logger.info("Please run ./start_with_patch.py to start the server with the patch applied.")
        else:
            logger.info("ForwardRef._evaluate already has recursive_guard parameter, no need to patch.")
    except Exception as e:
        logger.error(f"Error checking ForwardRef._evaluate: {e}")
        
        # Create a fallback monkey patch
        logger.info("Creating fallback monkey patch...")
        with open("monkey_patch_typing_fallback.py", 'w') as f:
            f.write("""
# Fallback monkey patch for typing.ForwardRef._evaluate
from typing import ForwardRef, Any, cast
import sys
import types

# Define a completely new _evaluate method
def new_evaluate(self, globalns, localns, recursive_guard=None):
    if recursive_guard is None:
        recursive_guard = set()
    
    if self.__forward_evaluated__:
        return self.__forward_value__
    
    if not globalns:
        globalns = sys.modules[self.__module__].__dict__
    
    self.__forward_value__ = eval(self.__forward_code__, globalns, localns)
    self.__forward_evaluated__ = True
    return self.__forward_value__

# Apply the patch
ForwardRef._evaluate = new_evaluate

print("ForwardRef._evaluate replaced with fallback implementation")
""")
        
        # Create a fallback startup script
        logger.info("Creating fallback startup script...")
        with open("start_with_fallback.py", 'w') as f:
            f.write("""#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the fallback monkey patch before importing anything else
print("Applying ForwardRef._evaluate fallback patch...")
exec(open("monkey_patch_typing_fallback.py").read())

# Start the server
port = 8001
if len(sys.argv) > 1:
    port = sys.argv[1]

print(f"Starting server on port {port}...")
# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/python"),
    "-c",
    "import sys; sys.path.insert(0, '.'); import monkey_patch_typing_fallback; from uvicorn.main import main; sys.argv = ['uvicorn', 'src.main:app', '--reload', '--port', '" + str(port) + "']; main()",
])
""")
        
        # Make the fallback startup script executable
        os.chmod("start_with_fallback.py", 0o755)
        
        logger.info("Fallback fix completed!")
        logger.info("Please run ./start_with_fallback.py to start the server with the fallback patch applied.")

if __name__ == "__main__":
    main()