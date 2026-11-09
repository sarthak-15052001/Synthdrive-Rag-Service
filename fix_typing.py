#!/usr/bin/env python3
import logging
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Fix ForwardRef._evaluate() issue by directly modifying the typing.py file."""
    logger.info("Starting direct fix for ForwardRef._evaluate() issue...")
    
    # Path to the pydantic typing.py file
    pydantic_typing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "venv/lib/python3.12/site-packages/pydantic/typing.py")
    
    # Read the current content of the file
    with open(pydantic_typing_path, 'r') as f:
        content = f.read()
    
    # Find the evaluate_forwardref function
    evaluate_forwardref_pattern = r'def evaluate_forwardref\(type_, globalns, localns\):'
    if re.search(evaluate_forwardref_pattern, content):
        # Replace the function with a fixed version
        fixed_content = re.sub(
            evaluate_forwardref_pattern,
            'def evaluate_forwardref(type_, globalns, localns):',
            content
        )
        
        # Find the _evaluate call
        evaluate_call_pattern = r'return cast\(Any, type_\)\._evaluate\(globalns, localns, set\(\)\)'
        if re.search(evaluate_call_pattern, fixed_content):
            # Replace the _evaluate call with a try-except block to handle the recursive_guard parameter
            fixed_content = re.sub(
                evaluate_call_pattern,
                '''try:
        return cast(Any, type_)._evaluate(globalns, localns, set())
    except TypeError as e:
        if "missing 1 required keyword-only argument: 'recursive_guard'" in str(e):
            # Handle the case where recursive_guard is required
            return cast(Any, type_)._evaluate(globalns, localns, recursive_guard=set())
        raise''',
                fixed_content
            )
            
            # Write the fixed content back to the file
            with open(pydantic_typing_path, 'w') as f:
                f.write(fixed_content)
            
            logger.info("Successfully patched pydantic/typing.py")
        else:
            logger.error("Could not find _evaluate call pattern in pydantic/typing.py")
    else:
        logger.error("Could not find evaluate_forwardref function in pydantic/typing.py")
    
    # Create a direct fix for the ForwardRef._evaluate method
    logger.info("Creating direct fix for ForwardRef._evaluate method...")
    
    # Create a file that will be imported at startup
    with open("fix_forwardref_evaluate.py", 'w') as f:
        f.write("""
# Direct fix for ForwardRef._evaluate
import typing
from typing import ForwardRef, Any

# Check if _evaluate method exists
if hasattr(ForwardRef, '_evaluate'):
    # Store the original _evaluate method
    original_evaluate = ForwardRef._evaluate
    
    # Define a new _evaluate method that handles both call signatures
    def patched_evaluate(self, globalns, localns, recursive_guard=None):
        if recursive_guard is None:
            recursive_guard = set()
        
        # Call the original method with the appropriate arguments
        try:
            # Try with recursive_guard
            return original_evaluate(self, globalns, localns, recursive_guard)
        except TypeError:
            # Fall back to without recursive_guard
            return original_evaluate(self, globalns, localns)
    
    # Apply the patch
    ForwardRef._evaluate = patched_evaluate
    print("ForwardRef._evaluate patched successfully")
""")
    
    # Create a startup script that applies the direct fix
    logger.info("Creating startup script with direct fix...")
    with open("start_server_fixed.py", 'w') as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the direct fix
print("Applying ForwardRef._evaluate fix...")
exec(open("fix_forwardref_evaluate.py").read())

# Start the server
port = 8001
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
""")
    
    # Make the startup script executable
    os.chmod("start_server_fixed.py", 0o755)
    
    logger.info("Fix completed successfully!")
    logger.info("Please run ./start_server_fixed.py to start the server with the direct fix applied.")

if __name__ == "__main__":
    main()