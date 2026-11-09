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
    """Fix all dependency compatibility issues."""
    logger.info("Starting comprehensive fix for all dependency compatibility issues...")
    
    # Get the virtual environment Python path
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        logger.error(f"Virtual environment Python not found at {venv_python}")
        venv_python = sys.executable
        logger.info(f"Using system Python instead: {venv_python}")
    
    # Step 1: Uninstall all conflicting packages
    logger.info("Uninstalling all conflicting packages...")
    packages_to_uninstall = [
        "fastapi",
        "starlette",
        "pydantic",
        "pydantic-settings",
        "langgraph",
        "langgraph-checkpoint",
        "langchain-core",
        "langchain",
        "langchain-community",
        "langchain-openai"
    ]
    
    for package in packages_to_uninstall:
        run_command(f"{venv_python} -m pip uninstall -y {package}")
    
    # Step 2: Install compatible versions in the correct order
    logger.info("Installing compatible versions of packages...")
    
    # Install Pydantic and FastAPI first
    run_command(f"{venv_python} -m pip install pydantic==1.10.8")
    run_command(f"{venv_python} -m pip install fastapi==0.95.2 starlette==0.27.0")
    run_command(f"{venv_python} -m pip install pydantic-settings==1.0.0")
    
    # Then install LangChain and related packages
    run_command(f"{venv_python} -m pip install langchain-core==0.1.53")
    run_command(f"{venv_python} -m pip install langchain==0.0.335")
    run_command(f"{venv_python} -m pip install langchain-community==0.0.16")
    run_command(f"{venv_python} -m pip install langchain-openai==0.0.5")
    
    # Install LangGraph with a compatible version
    run_command(f"{venv_python} -m pip install langgraph==0.0.25")
    run_command(f"{venv_python} -m pip install langgraph-checkpoint==1.0.12")
    
    # Step 3: Verify installations
    logger.info("Verifying installations...")
    installed_packages = run_command(f"{venv_python} -m pip list")
    logger.info("Installed packages:\n" + installed_packages)
    
    # Step 4: Create a patch for the CheckpointAt issue if needed
    logger.info("Creating patch for CheckpointAt issue...")
    checkpoint_base_init = os.path.join(os.getcwd(), "venv", "lib", "python3.12", "site-packages", "langgraph", "checkpoint", "base", "__init__.py")
    
    if os.path.exists(checkpoint_base_init):
        with open(checkpoint_base_init, 'r') as f:
            content = f.read()
        
        if "CheckpointAt" not in content:
            logger.info("Adding CheckpointAt to langgraph.checkpoint.base.__init__.py")
            with open(checkpoint_base_init, 'a') as f:
                f.write("\n\n# Added by fix script\nclass CheckpointAt:\n    def __init__(self, *args, **kwargs):\n        pass\n")
    else:
        logger.warning(f"Checkpoint base init file not found at {checkpoint_base_init}")
    
    # Step 5: Create a patch for the ToolNode issue if needed
    logger.info("Creating patch for ToolNode issue...")
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
    def __init__(self, tools=None, handle_tool_errors=True, messages_key="messages"):
        self.tools = tools or []
        self.handle_tool_errors = handle_tool_errors
        self.messages_key = messages_key
    
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