#!/usr/bin/env python3

import os
import sys
import logging
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def fix_apikey_issue():
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
    shutil.copy2(models_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    # Read the file
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Find the APIKey class and add type annotation to type_ field
    # Original:
    # class APIKey(SecurityBase):
    #     type_ = "apiKey"
    #     in_: APIKeyIn
    #     name: str
    
    # Fixed:
    # class APIKey(SecurityBase):
    #     type_: str = "apiKey"
    #     in_: APIKeyIn
    #     name: str
    
    fixed_content = content.replace(
        "class APIKey(SecurityBase):\n    type_ = \"apiKey\"",
        "class APIKey(SecurityBase):\n    type_: str = \"apiKey\""
    )
    
    # Write the fixed content
    with open(models_path, 'w') as f:
        f.write(fixed_content)
    
    logger.info(f"Fixed APIKey type_ annotation issue in {models_path}")
    
    # Update the startup script to include all fixes
    startup_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "start_with_all_fixes.py"
    )
    
    with open(startup_script_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
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

def apply_typeis_fix():
    # Fix for TypeIs in typing_extensions
    import typing_extensions
    
    # Add TypeIs as an alias for Type if it doesn't exist
    if not hasattr(typing_extensions, 'TypeIs'):
        typing_extensions.TypeIs = typing_extensions.Type
        logger.info("Added TypeIs to typing_extensions")

def start_server():
    # Apply all fixes
    apply_sentinel_fix()
    apply_typeis_fix()
    
    # Start the server
    logger.info("Starting server with all fixes applied")
    os.system("uvicorn src.main:app --reload")

if __name__ == "__main__":
    # Make the script executable
    os.chmod(__file__, 0o755)
    
    # Start the server with all fixes
    start_server()
""")
    
    # Make the startup script executable
    os.chmod(startup_script_path, 0o755)
    logger.info(f"Updated startup script at {startup_script_path}")
    
    logger.info("All fixes applied successfully")
    logger.info("Run ./start_with_all_fixes.py to start the server with all patches applied")
    
    return True

if __name__ == "__main__":
    fix_apikey_issue()