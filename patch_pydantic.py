#!/usr/bin/env python3
import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Patch the pydantic typing.py file to fix the ForwardRef._evaluate issue."""
    logger.info("Starting pydantic typing.py patch...")
    
    # Find the pydantic typing.py file in the virtual environment
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    site_packages = None
    
    for root, dirs, files in os.walk(venv_path):
        if "site-packages" in root and "pydantic" in dirs:
            site_packages = root
            break
    
    if not site_packages:
        logger.error("Could not find site-packages directory in the virtual environment.")
        return
    
    pydantic_typing_path = os.path.join(site_packages, "pydantic", "typing.py")
    
    if not os.path.exists(pydantic_typing_path):
        logger.error(f"Could not find pydantic typing.py at {pydantic_typing_path}")
        return
    
    logger.info(f"Found pydantic typing.py at {pydantic_typing_path}")
    
    # Create a backup of the original file
    backup_path = pydantic_typing_path + ".bak"
    if not os.path.exists(backup_path):
        logger.info(f"Creating backup at {backup_path}")
        with open(pydantic_typing_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
    
    # Read the file content
    with open(pydantic_typing_path, 'r') as f:
        content = f.read()
    
    # Find the evaluate_forwardref function
    evaluate_forwardref_pattern = re.compile(r'def evaluate_forwardref\(type_: ForwardRef, globalns: Any, localns: Optional\[Dict\[str, Any\]\]\) -> Any:.*?return cast\(Any, type_\)\._evaluate\(globalns, localns, set\(\)\)', re.DOTALL)
    
    match = evaluate_forwardref_pattern.search(content)
    if not match:
        logger.error("Could not find evaluate_forwardref function in pydantic typing.py")
        return
    
    # Replace the function with a fixed version
    original_function = match.group(0)
    fixed_function = """def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Optional[Dict[str, Any]]) -> Any:
    """
    fixed_function += """
    # Check if _evaluate accepts recursive_guard parameter
    import inspect
    sig = inspect.signature(type_._evaluate)
    if 'recursive_guard' in sig.parameters:
        return cast(Any, type_)._evaluate(globalns, localns, set())
    else:
        # Fall back to the old signature
        return cast(Any, type_)._evaluate(globalns, localns)
    """
    
    new_content = content.replace(original_function, fixed_function)
    
    # Write the modified content back to the file
    with open(pydantic_typing_path, 'w') as f:
        f.write(new_content)
    
    logger.info("Successfully patched pydantic typing.py")
    
    # Create a startup script
    startup_script = """#!/usr/bin/env python3
import os
import sys
import subprocess

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
    
    with open("start_patched_server.py", 'w') as f:
        f.write(startup_script)
    
    # Make the startup script executable
    os.chmod("start_patched_server.py", 0o755)
    
    logger.info("Created start_patched_server.py")
    logger.info("Please run ./start_patched_server.py to start the server with the patched pydantic typing.py")

if __name__ == "__main__":
    main()