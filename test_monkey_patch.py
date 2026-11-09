# First run the monkey patch
import monkey_patch

# Then try to import CheckpointAt from langgraph.checkpoint.base
try:
    from langgraph.checkpoint.base import CheckpointAt
    print("Successfully imported CheckpointAt from langgraph.checkpoint.base")
    
    # Print the values of the enum
    print("\nCheckpointAt values:")
    for value in CheckpointAt:
        print(f"- {value.name}: {value.value}")
    
    # Test calling the enum
    print("\nTesting calling CheckpointAt.END:")
    result = CheckpointAt.END()
    print(f"Result: {result}")
    
except Exception as e:
    print(f"Error: {e}")