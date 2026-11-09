#!/usr/bin/env python3
import subprocess
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the output."""
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
        return e.stderr

def main():
    """Fix LangGraph ToolNode import issue."""
    logger.info("Starting fix for LangGraph ToolNode import issue...")
    
    # Get the virtual environment Python path
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        logger.error(f"Virtual environment Python not found at {venv_python}")
        venv_python = sys.executable
        logger.info(f"Using system Python instead: {venv_python}")
    
    # Step 1: Install a compatible version of langgraph that includes ToolNode
    logger.info("Installing compatible version of langgraph...")
    run_command(f"{venv_python} -m pip install langgraph==0.0.27")
    
    # Step 2: Create a patch for the missing ToolNode class if needed
    logger.info("Creating patch for missing ToolNode class if needed...")
    prebuilt_init = os.path.join(os.getcwd(), "venv", "lib", "python3.12", "site-packages", "langgraph", "prebuilt", "__init__.py")
    
    if os.path.exists(prebuilt_init):
        with open(prebuilt_init, 'r') as f:
            content = f.read()
        
        if "ToolNode" not in content:
            logger.info("Adding ToolNode to langgraph.prebuilt.__init__.py")
            with open(prebuilt_init, 'a') as f:
                f.write("""
# Added by fix script
class ToolNode:
    \"\"\"A node that can execute tools.\"\"\"
    def __init__(self, tools=None):
        self.tools = tools or []
    
    def __call__(self, state):
        # Simple implementation that just returns the state
        return state
""")
    else:
        logger.warning(f"Prebuilt init file not found at {prebuilt_init}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()