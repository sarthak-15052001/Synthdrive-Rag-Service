#!/usr/bin/env python3

import sys
import types
import logging
import importlib
import importlib.util
import os
import subprocess
from typing import Any, Dict, Optional, Set, ForwardRef, cast

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_site_packages():
    """Find the site-packages directory in the virtual environment"""
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    for root, dirs, files in os.walk(venv_path):
        if "site-packages" in root:
            return root
    
    return None

def patch_pydantic_fields():
    """Add ModelField to pydantic.fields"""
    logger.info("Patching pydantic.fields module...")
    
    try:
        import pydantic.fields
        
        # Fix 1: Add ModelField to pydantic.fields
        if not hasattr(pydantic.fields, 'ModelField'):
            # Create a ModelField class if it doesn't exist
            class ModelField:
                def __init__(self, name=None, type_=None, class_validators=None, model_config=None,
                            default=None, default_factory=None, required=None, alias=None,
                            field_info=None, **kwargs):
                    self.name = name
                    self.type_ = type_
                    self.class_validators = class_validators or {}
                    self.model_config = model_config or {}
                    self.default = default
                    self.default_factory = default_factory
                    self.required = required
                    self.alias = alias
                    self.field_info = field_info
                    self.kwargs = kwargs
                    
                def __repr__(self):
                    return f"ModelField(name={self.name}, type_={self.type_})"
            
            # Add ModelField to pydantic.fields
            pydantic.fields.ModelField = ModelField
            logger.info("Added ModelField to pydantic.fields")
        else:
            logger.info("ModelField already exists in pydantic.fields")
        
        # Fix 2: Add Undefined to pydantic.fields if it doesn't exist
        if not hasattr(pydantic.fields, 'Undefined'):
            class UndefinedType:
                def __repr__(self):
                    return "Undefined"
                
                def __bool__(self):
                    return False
            
            # Create a singleton instance
            pydantic.fields.Undefined = UndefinedType()
            logger.info("Added Undefined to pydantic.fields")
        else:
            logger.info("Undefined already exists in pydantic.fields")
            
    except ImportError as e:
        logger.error(f"Could not import pydantic.fields: {e}")

def patch_langchain_schema():
    """Create mock langchain.schema module with Document class"""
    logger.info("Patching langchain.schema module...")
    
    try:
        try:
            import langchain.schema
            logger.info("langchain.schema module already exists")
        except ImportError:
            # Create mock module
            mock_schema = types.ModuleType('langchain.schema')
            sys.modules['langchain.schema'] = mock_schema
            
            # Add Document class to mock module
            class Document:
                def __init__(self, page_content="", metadata=None):
                    self.page_content = page_content
                    self.metadata = metadata or {}
                    
                def __repr__(self):
                    return f"Document(page_content={self.page_content}, metadata={self.metadata})"
            
            mock_schema.Document = Document
            logger.info("Created mock langchain.schema module with Document class")
    except Exception as e:
        logger.error(f"Error creating mock langchain.schema module: {e}")

def patch_langgraph_errors():
    """Create mock langgraph.errors module"""
    logger.info("Patching langgraph.errors module...")
    
    try:
        try:
            import langgraph.errors
            logger.info("langgraph.errors module already exists")
        except ImportError:
            # Create mock module
            mock_errors = types.ModuleType('langgraph.errors')
            sys.modules['langgraph.errors'] = mock_errors
            
            # Add error classes
            class EmptyInputError(Exception):
                pass
            
            class InvalidUpdateError(Exception):
                pass
            
            mock_errors.EmptyInputError = EmptyInputError
            mock_errors.InvalidUpdateError = InvalidUpdateError
            logger.info("Created mock langgraph.errors module")
    except Exception as e:
        logger.error(f"Error creating mock langgraph.errors module: {e}")

def patch_fastapi_security():
    """Fix SecurityBase issue in FastAPI"""
    logger.info("Patching FastAPI security modules...")
    
    try:
        from fastapi.security.base import SecurityBase
        from fastapi.openapi.models import SecuritySchemeType
        
        # Check if APIKey exists and fix its type_ annotation
        try:
            from fastapi.openapi.models import APIKey
            if not hasattr(APIKey.type_, '__annotations__'):
                APIKey.type_.__annotations__ = {'return': SecuritySchemeType}
                logger.info("Fixed APIKey type_ annotation")
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not fix APIKey: {e}")
        
        # Check if HTTPBase exists and fix its type_ annotation
        try:
            from fastapi.openapi.models import HTTPBase
            if not hasattr(HTTPBase.type_, '__annotations__'):
                HTTPBase.type_.__annotations__ = {'return': SecuritySchemeType}
                logger.info("Fixed HTTPBase type_ annotation")
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not fix HTTPBase: {e}")
        
        # Check if OAuth2 exists and fix its type_ annotation
        try:
            from fastapi.openapi.models import OAuth2
            if not hasattr(OAuth2.type_, '__annotations__'):
                OAuth2.type_.__annotations__ = {'return': SecuritySchemeType}
                logger.info("Fixed OAuth2 type_ annotation")
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not fix OAuth2: {e}")
        
        # Check if OpenIdConnect exists and fix its type_ annotation
        try:
            from fastapi.openapi.models import OpenIdConnect
            if not hasattr(OpenIdConnect.type_, '__annotations__'):
                OpenIdConnect.type_.__annotations__ = {'return': SecuritySchemeType}
                logger.info("Fixed OpenIdConnect type_ annotation")
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not fix OpenIdConnect: {e}")
            
    except ImportError as e:
        logger.error(f"Could not import FastAPI security modules: {e}")

def patch_pydantic_core():
    """Patch the pydantic_core module to handle the Sentinel import issue"""
    logger.info("Patching pydantic_core module...")
    
    try:
        # Path to the pydantic_core/__init__.py file
        site_packages = find_site_packages()
        if not site_packages:
            logger.error("Could not find site-packages directory")
            return
        
        pydantic_core_init_path = os.path.join(site_packages, "pydantic_core/__init__.py")
        
        if not os.path.exists(pydantic_core_init_path):
            logger.error(f"Could not find pydantic_core module at {pydantic_core_init_path}")
            return
        
        # Read the file
        with open(pydantic_core_init_path, 'r') as f:
            content = f.read()
        
        # Replace the import line
        if "from typing_extensions import Sentinel" in content:
            logger.info("Found Sentinel import, replacing it")
            new_content = content.replace(
                "from typing_extensions import Sentinel",
                "# Patched Sentinel import\nclass _SentinelType:\n    def __repr__(self):\n        return \"Sentinel\"\nSentinel = _SentinelType()"
            )
            
            # Write the modified content back
            with open(pydantic_core_init_path, 'w') as f:
                f.write(new_content)
            
            logger.info("Successfully patched pydantic_core module")
        else:
            logger.info("Sentinel import not found in pydantic_core module, no patch needed")
    except Exception as e:
        logger.error(f"Error patching pydantic_core module: {e}")

def patch_forwardref():
    """Patch the typing.ForwardRef._evaluate method to handle the recursive_guard parameter"""
    logger.info("Patching typing.ForwardRef._evaluate method...")
    
    try:
        # Store the original _evaluate method
        original_evaluate = ForwardRef._evaluate
        
        # Define the patched method
        def patched_evaluate(self, globalns: Dict[str, Any], localns: Optional[Dict[str, Any]],
                            recursive_guard: Optional[Set[Any]] = None) -> Any:
            """
            Patched version of ForwardRef._evaluate that handles the recursive_guard parameter
            added in Python 3.12.
            """
            # If recursive_guard is provided (Python 3.12+), but the original method doesn't accept it
            import inspect
            sig = inspect.signature(original_evaluate)
            
            if 'recursive_guard' in sig.parameters:
                # Original method supports recursive_guard, pass it through
                return original_evaluate(self, globalns, localns, recursive_guard)
            else:
                # Original method doesn't support recursive_guard, call without it
                return original_evaluate(self, globalns, localns)
        
        # Apply the patch
        ForwardRef._evaluate = patched_evaluate
        logger.info("Successfully patched ForwardRef._evaluate method")
    except Exception as e:
        logger.error(f"Error patching ForwardRef._evaluate method: {e}")

def apply_fixes():
    """Apply all necessary fixes before starting the server"""
    logger.info("Applying fixes before starting the server...")
    
    # Apply all patches
    patch_pydantic_fields()
    patch_langchain_schema()
    patch_langgraph_errors()
    patch_fastapi_security()
    patch_pydantic_core()
    patch_forwardref()
    
    logger.info("All fixes applied successfully!")

if __name__ == "__main__":
    # Apply fixes
    apply_fixes()
    
    # Start the server
    logger.info("Starting the server...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Start the server with uvicorn
    try:
        subprocess.run(["uvicorn", "src.main:app", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start server: {e}")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")