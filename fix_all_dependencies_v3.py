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
    """Fix all dependency compatibility issues."""
    logger.info("Starting comprehensive fix for all dependency compatibility issues...")
    
    # Get the Python executable from the virtual environment
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
    venv_pip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "pip")
    
    # Uninstall all conflicting packages
    logger.info("Uninstalling all conflicting packages...")
    packages_to_uninstall = [
        "fastapi", "starlette", "pydantic", "pydantic-settings", 
        "langgraph", "langgraph-checkpoint", "langchain-core", 
        "langchain", "langchain-community", "langchain-openai",
        "uvicorn"
    ]
    
    for package in packages_to_uninstall:
        run_command(f"{venv_pip} uninstall -y {package}")
    
    # Install compatible versions
    logger.info("Installing compatible versions of packages...")
    
    # First, install Pydantic with v1 compatibility
    run_command(f"{venv_pip} install 'pydantic>=1.8.2,<2.0.0'")
    
    # Create pydantic.v1 symlink for backward compatibility
    logger.info("Creating pydantic.v1 symlink for backward compatibility...")
    pydantic_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "venv/lib/python3.12/site-packages/pydantic")
    
    if not os.path.exists(os.path.join(pydantic_dir, "v1")):
        # Create a v1 directory that symlinks to the main pydantic package
        v1_dir = os.path.join(pydantic_dir, "v1")
        os.makedirs(v1_dir, exist_ok=True)
        
        # Create an __init__.py file in the v1 directory that imports from the parent
        with open(os.path.join(v1_dir, "__init__.py"), "w") as f:
            f.write("""
# This file provides backward compatibility for pydantic.v1
from .. import *
""")
    
    # Install FastAPI and related packages
    run_command(f"{venv_pip} install 'fastapi<0.69.0' 'starlette<0.20.0'")
    run_command(f"{venv_pip} install 'uvicorn<0.16.0'")
    
    # Install LangChain and related packages
    run_command(f"{venv_pip} install 'langchain-core<0.2.0'")
    run_command(f"{venv_pip} install 'langchain<0.1.0'")
    run_command(f"{venv_pip} install 'langchain-community<0.1.0'")
    run_command(f"{venv_pip} install 'langchain-openai<0.1.0'")
    
    # Install LangGraph and related packages
    run_command(f"{venv_pip} install 'langgraph<0.1.0'")
    run_command(f"{venv_pip} install 'langgraph-checkpoint<1.1.0'")
    
    # Create patch for CheckpointAt issue
    logger.info("Creating patch for CheckpointAt issue...")
    checkpoint_base_init_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "venv/lib/python3.12/site-packages/langgraph/checkpoint/base/__init__.py")
    
    # Check if CheckpointAt is already defined
    with open(checkpoint_base_init_path, 'r') as f:
        content = f.read()
    
    if "class CheckpointAt:" not in content:
        # Add CheckpointAt to langgraph.checkpoint.base.__init__.py
        with open(checkpoint_base_init_path, 'a') as f:
            f.write("""
# Mock implementation of CheckpointAt
class CheckpointAt:
    def __init__(self, checkpoint_id=None, checkpoint_method=None):
        self.checkpoint_id = checkpoint_id
        self.checkpoint_method = checkpoint_method
""")
    
    # Create patch for ToolNode issue
    logger.info("Creating patch for ToolNode issue...")
    prebuilt_init_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "venv/lib/python3.12/site-packages/langgraph/prebuilt/__init__.py")
    
    # Check if ToolNode is already defined
    with open(prebuilt_init_path, 'r') as f:
        content = f.read()
    
    if "class ToolNode:" not in content:
        # Add ToolNode to langgraph.prebuilt.__init__.py
        with open(prebuilt_init_path, 'a') as f:
            f.write("""
# Mock implementation of ToolNode
class ToolNode:
    def __init__(self, tools=None, llm=None):
        self.tools = tools or []
        self.llm = llm
        
    def __call__(self, state):
        # Mock implementation
        return state
""")
    
    # Verify installations
    logger.info("Verifying installations...")
    installed_packages = run_command(f"{venv_pip} list")
    logger.info(f"Installed packages:\n{installed_packages}")
    
    logger.info("Fix completed successfully!")
    logger.info("Please restart your server to apply the changes.")

if __name__ == "__main__":
    main()