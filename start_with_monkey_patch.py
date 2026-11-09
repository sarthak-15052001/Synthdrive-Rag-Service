#!/usr/bin/env python3
import os
import sys
import subprocess

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the monkey patch before anything else
import fix_forwardref_monkey

# Start the server
port = 8000
if len(sys.argv) > 1:
    port = sys.argv[1]

print(f"Starting server on port {port}...")
# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/uvicorn"),
    "src.main:app",
    "--reload",
    "--port", str(port)
])
