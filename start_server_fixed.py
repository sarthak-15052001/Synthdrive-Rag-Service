#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the direct fix
print("Applying ForwardRef._evaluate fix...")
exec(open("fix_forwardref_evaluate.py").read())

# Start the server
port = 8001
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
