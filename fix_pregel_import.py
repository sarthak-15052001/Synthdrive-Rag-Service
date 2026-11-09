"""
This script fixes the import of CheckpointAt in langgraph.pregel.__init__.py.
"""

import os

# Find the langgraph package
import langgraph
langgraph_path = os.path.dirname(langgraph.__file__)
pregel_init_path = os.path.join(langgraph_path, 'pregel', '__init__.py')

# Read the current content of the file
with open(pregel_init_path, 'r') as f:
    content = f.read()

# Replace the import line
modified_content = content.replace(
    "from langgraph.checkpoint.base import (\n    BaseCheckpointSaver,\n    Checkpoint,\n    CheckpointAt,\n    empty_checkpoint,\n)",
    "from langgraph.checkpoint.base import (\n    BaseCheckpointSaver,\n    Checkpoint,\n    empty_checkpoint,\n)\nfrom langgraph.checkpoint import CheckpointAt"
)

# Write the modified content back to the file
with open(pregel_init_path, 'w') as f:
    f.write(modified_content)

print(f"Fixed import in {pregel_init_path}")