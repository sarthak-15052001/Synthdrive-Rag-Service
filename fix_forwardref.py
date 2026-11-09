#!/usr/bin/env python3
import logging
import subprocess
import sys
import os
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a command and return its output."""
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
        return None

def main():
    """Fix ForwardRef._evaluate() issue."""
    logger.info("Starting fix for ForwardRef._evaluate() issue...")
    
    # Get the Python executable from the virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    venv_pip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "pip")
    
    # Patch the typing.py file to fix the ForwardRef._evaluate() issue
    logger.info("Patching pydantic/typing.py to fix ForwardRef._evaluate() issue...")
    pydantic_typing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "venv/lib/python3.12/site-packages/pydantic/typing.py")
    
    # Read the current content of the file
    with open(pydantic_typing_path, 'r') as f:
        content = f.read()
    
    # Check if the function needs to be patched
    if "def evaluate_forwardref(type_, globalns, localns):" in content:
        # Replace the evaluate_forwardref function with a patched version
        patched_content = content.replace(
            "def evaluate_forwardref(type_, globalns, localns):",
            """def evaluate_forwardref(type_, globalns, localns):
    # Add recursive_guard parameter with default value
    recursive_guard = set()"""
        )
        
        patched_content = patched_content.replace(
            "return cast(Any, type_)._evaluate(globalns, localns, set())",
            "return cast(Any, type_)._evaluate(globalns, localns, recursive_guard)"
        )
        
        # Write the patched content back to the file
        with open(pydantic_typing_path, 'w') as f:
            f.write(patched_content)
        
        logger.info("Successfully patched pydantic/typing.py")
    else:
        logger.info("No need to patch pydantic/typing.py, function signature not found")
    
    # Also patch the ForwardRef class in typing.py if needed
    logger.info("Checking if ForwardRef._evaluate() needs patching...")
    typing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "venv/lib/python3.12/site-packages/typing.py")
    
    if os.path.exists(typing_path):
        with open(typing_path, 'r') as f:
            typing_content = f.read()
        
        if "_evaluate(self, globalns, localns)" in typing_content:
            # Patch the _evaluate method to accept the recursive_guard parameter
            patched_typing_content = typing_content.replace(
                "_evaluate(self, globalns, localns)",
                "_evaluate(self, globalns, localns, recursive_guard=None)"
            )
            
            # Write the patched content back to the file
            with open(typing_path, 'w') as f:
                f.write(patched_typing_content)
            
            logger.info("Successfully patched typing.py")
        else:
            logger.info("No need to patch typing.py, method signature not found")
    else:
        logger.info("typing.py not found, skipping patch")
    
    # Create a monkey patch for ForwardRef._evaluate
    logger.info("Creating monkey patch for ForwardRef._evaluate...")
    monkey_patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monkey_patch_forwardref.py")
    
    with open(monkey_patch_path, 'w') as f:
        f.write("""
# Monkey patch for ForwardRef._evaluate
import typing
from typing import ForwardRef

# Store the original _evaluate method
original_evaluate = ForwardRef._evaluate

# Define a new _evaluate method that accepts the recursive_guard parameter
def patched_evaluate(self, globalns, localns, recursive_guard=None):
    if recursive_guard is None:
        recursive_guard = set()
    return original_evaluate(self, globalns, localns)

# Apply the monkey patch
ForwardRef._evaluate = patched_evaluate

print("ForwardRef._evaluate monkey patch applied successfully")
""")
    
    # Create a patch for the Undefined issue
    logger.info("Creating patch for Undefined issue...")
    pydantic_fields_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "venv/lib/python3.12/site-packages/pydantic/fields.py")
    
    # Add Undefined class to pydantic.fields if it doesn't exist
    with open(pydantic_fields_path, 'r') as f:
        fields_content = f.read()
    
    if "class Undefined:" not in fields_content:
        with open(pydantic_fields_path, 'a') as f:
            f.write("""
# Mock implementation of Undefined
class Undefined:
    def __repr__(self):
        return 'Undefined'
    
    def __bool__(self):
        return False

# Create a singleton instance
Undefined = Undefined()
""")
        logger.info("Added Undefined class to pydantic/fields.py")
    else:
        logger.info("Undefined class already exists in pydantic/fields.py")
    
    # Create a startup script that applies the monkey patch
    logger.info("Creating startup script...")
    startup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_server.py")
    
    with open(startup_script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the monkey patch
exec(open("monkey_patch_forwardref.py").read())

# Start the server
port = 8001
if len(sys.argv) > 1:
    port = sys.argv[1]

# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/uvicorn"),
    "src.main:app",
    "--reload",
    "--port", str(port)
])
""")
    
    # Make the startup script executable
    os.chmod(startup_script_path, 0o755)
    
    logger.info("Fix completed successfully!")
    logger.info("Please run ./start_server.py to start the server with the patches applied.")

if __name__ == "__main__":
    main()