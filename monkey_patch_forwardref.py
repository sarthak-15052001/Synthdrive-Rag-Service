
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
