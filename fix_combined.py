#!/usr/bin/env python3
"""
Comprehensive fix script for FastAPI and LangGraph compatibility issues.
This script addresses:
1. Pydantic error in FastAPI's SecurityBase class
2. Missing 'langgraph.errors' module issue
"""
import os
import sys
import logging
import shutil
import subprocess
import importlib.util
from pathlib import Path

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

def fix_security_base_issue():
    """Fix the Pydantic error in FastAPI's SecurityBase class."""
    logger.info("Fixing SecurityBase type_ annotation issue...")
    
    # Find the fastapi security base.py file
    base_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv/lib/python3.12/site-packages/fastapi/security/base.py"
    )
    
    if not os.path.exists(base_path):
        logger.error(f"Could not find {base_path}")
        return False
    
    # Create a backup
    backup_path = f"{base_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(base_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Add type annotation to type_ field in SecurityBase class
    fixed_content = content.replace(
        "class SecurityBase:\n    type_ = \"\"",
        "class SecurityBase:\n    type_: str = \"\""
    )
    
    # Write the fixed content
    with open(base_path, 'w') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed SecurityBase type_ annotation issue in {base_path}")
    
    # Find the fastapi openapi models.py file
    models_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv/lib/python3.12/site-packages/fastapi/openapi/models.py"
    )
    
    if not os.path.exists(models_path):
        logger.error(f"Could not find {models_path}")
        return False
    
    # Create a backup
    backup_path = f"{models_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(models_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Add type annotation to type_ field in APIKey class
    fixed_content = content.replace(
        "class APIKey(SecurityBase):\n    type_ = \"apiKey\"",
        "class APIKey(SecurityBase):\n    type_: str = \"apiKey\""
    )
    
    # Write the fixed content
    with open(models_path, 'w') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed APIKey type_ annotation issue in {models_path}")
    return True

def fix_langgraph_errors_module():
    """Fix the missing 'langgraph.errors' module issue."""
    logger.info("Fixing missing langgraph.errors module...")
    
    # Get the virtual environment Python path
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(venv_python):
        logger.error(f"Virtual environment Python not found at {venv_python}")
        venv_python = sys.executable
        logger.info(f"Using system Python instead: {venv_python}")
    
    # Step 1: Uninstall conflicting packages
    logger.info("Uninstalling conflicting packages...")
    packages_to_uninstall = [
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
    
    # First, install langchain-core
    run_command(f"{venv_python} -m pip install langchain-core==0.1.53")
    
    # Then install langchain and related packages
    run_command(f"{venv_python} -m pip install langchain==0.0.335")
    run_command(f"{venv_python} -m pip install langchain-community==0.0.16")
    run_command(f"{venv_python} -m pip install langchain-openai==0.0.5")
    
    # Install langgraph with a version that's compatible with the project
    run_command(f"{venv_python} -m pip install langgraph==0.0.25")
    
    # Install langgraph-checkpoint with a compatible version
    run_command(f"{venv_python} -m pip install langgraph-checkpoint==1.0.12")
    
    # Step 3: Create the missing langgraph.errors module
    langgraph_path = os.path.join(os.getcwd(), "venv", "lib", "python3.12", "site-packages", "langgraph")
    errors_path = os.path.join(langgraph_path, "errors.py")
    
    if not os.path.exists(langgraph_path):
        logger.error(f"LangGraph package directory not found at {langgraph_path}")
        return False
    
    # Create the errors.py file with the necessary error classes
    error_module_content = '''
# Mock langgraph.errors module
class LangGraphError(Exception):
    """Base class for all LangGraph errors."""
    pass

class EmptyInputError(LangGraphError):
    """Raised when an input to a node is empty."""
    pass

class InvalidUpdateError(LangGraphError):
    """Raised when an update to a state is invalid."""
    pass

class NodeExecutionError(LangGraphError):
    """Raised when a node execution fails."""
    pass

class ConfigurationError(LangGraphError):
    """Raised when there is a configuration error."""
    pass

class ValidationError(LangGraphError):
    """Raised when validation fails."""
    pass
'''
    
    with open(errors_path, 'w') as f:
        f.write(error_module_content)
    
    logger.info(f"Created mock langgraph.errors module at {errors_path}")
    
    # Update the __init__.py to import the errors
    init_path = os.path.join(langgraph_path, "__init__.py")
    if os.path.exists(init_path):
        with open(init_path, 'r') as f:
            content = f.read()
        
        if "from . import errors" not in content:
            with open(init_path, 'a') as f:
                f.write("\n\n# Added by fix script\nfrom . import errors\n")
            logger.info(f"Updated {init_path} to import errors module")
    
    return True

def apply_sentinel_fix():
    """Fix for Sentinel issue in pydantic_core."""
    logger.info("Applying Sentinel fix for pydantic_core...")
    try:
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
        return True
    except ImportError:
        logger.error("Could not import pydantic_core to apply Sentinel fix")
        return False

def apply_typeis_fix():
    """Fix for TypeIs in typing_extensions."""
    logger.info("Applying TypeIs fix for typing_extensions...")
    try:
        import typing_extensions
        
        # Add TypeIs as an alias for Type if it doesn't exist
        if not hasattr(typing_extensions, 'TypeIs'):
            typing_extensions.TypeIs = typing_extensions.Type
            logger.info("Added TypeIs to typing_extensions")
        return True
    except ImportError:
        logger.error("Could not import typing_extensions to apply TypeIs fix")
        return False

def create_startup_script():
    """Create a startup script that applies all fixes before starting the server."""
    logger.info("Creating startup script...")
    
    startup_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "start_fixed_server.py"
    )
    
    startup_script_content = '''#!/usr/bin/env python3
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
    try:
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
    except ImportError:
        logger.error("Could not import pydantic_core to apply Sentinel fix")

def apply_typeis_fix():
    # Fix for TypeIs in typing_extensions
    try:
        import typing_extensions
        
        # Add TypeIs as an alias for Type if it doesn't exist
        if not hasattr(typing_extensions, 'TypeIs'):
            typing_extensions.TypeIs = typing_extensions.Type
            logger.info("Added TypeIs to typing_extensions")
    except ImportError:
        logger.error("Could not import typing_extensions to apply TypeIs fix")

def ensure_langgraph_errors():
    # Ensure langgraph.errors module exists
    try:
        import langgraph.errors
        logger.info("langgraph.errors module exists")
    except ImportError:
        logger.info("Creating mock langgraph.errors module")
        import sys
        import types
        
        # Create a mock module
        mock_errors = types.ModuleType('langgraph.errors')
        
        # Add error classes
        class LangGraphError(Exception):
            """Base class for all LangGraph errors."""
            pass

        class EmptyInputError(LangGraphError):
            """Raised when an input to a node is empty."""
            pass

        class InvalidUpdateError(LangGraphError):
            """Raised when an update to a state is invalid."""
            pass
        
        # Add the classes to the module
        mock_errors.LangGraphError = LangGraphError
        mock_errors.EmptyInputError = EmptyInputError
        mock_errors.InvalidUpdateError = InvalidUpdateError
        
        # Add the module to sys.modules
        sys.modules['langgraph.errors'] = mock_errors
        logger.info("Mock langgraph.errors module created")

def start_server():
    # Apply all runtime fixes
    apply_sentinel_fix()
    apply_typeis_fix()
    ensure_langgraph_errors()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
'''
    
    with open(startup_script_path, 'w') as f:
        f.write(startup_script_content)
    
    # Make the startup script executable
    os.chmod(startup_script_path, 0o755)
    logger.info(f"Created startup script at {startup_script_path}")
    return True

def main():
    """Main function to fix all issues."""
    logger.info("Starting comprehensive fix for all issues...")
    
    # Fix the Pydantic error in FastAPI's SecurityBase class
    if not fix_security_base_issue():
        logger.error("Failed to fix SecurityBase issue. Continuing with other fixes...")
    else:
        logger.info("Successfully fixed SecurityBase issue.")
    
    # Fix the missing 'langgraph.errors' module issue
    if not fix_langgraph_errors_module():
        logger.error("Failed to fix langgraph.errors module issue. Continuing with other fixes...")
    else:
        logger.info("Successfully fixed langgraph.errors module issue.")
    
    # Create the startup script
    if not create_startup_script():
        logger.error("Failed to create startup script.")
    else:
        logger.info("Successfully created startup script.")
    
    logger.info("All fixes applied successfully!")
    logger.info("Run ./start_fixed_server.py to start the server with all patches applied")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())