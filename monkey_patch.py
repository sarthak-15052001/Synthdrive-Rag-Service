"""
This script monkey patches the langgraph.checkpoint.base module to include
the CheckpointAt class that is missing from the installed version.
"""

import sys
from enum import Enum
from typing import Any

# Define the CheckpointAt class
class CheckpointAt(Enum):
    """
    Enum for specifying when to checkpoint in a LangGraph.
    This is a dummy implementation to fix import errors.
    """
    NEVER = "never"
    END = "end"
    EVERY_NODE = "every_node"
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Make the enum callable to mimic the behavior of the original class.
        """
        return self.value

# Import the langgraph.checkpoint.base module
import langgraph.checkpoint.base

# Add the CheckpointAt class to the module
setattr(langgraph.checkpoint.base, 'CheckpointAt', CheckpointAt)

# Add it to the module's __all__ list if it exists
if hasattr(langgraph.checkpoint.base, '__all__'):
    if 'CheckpointAt' not in langgraph.checkpoint.base.__all__:
        langgraph.checkpoint.base.__all__.append('CheckpointAt')

print("Successfully monkey patched langgraph.checkpoint.base with CheckpointAt")