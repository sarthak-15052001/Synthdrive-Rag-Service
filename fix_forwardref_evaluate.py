
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
