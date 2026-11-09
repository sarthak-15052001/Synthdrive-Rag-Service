#!/usr/bin/env python3
import os
import sys
import subprocess

# Apply the monkey patch
exec(open("monkey_patch_forwardref.py").read())

# Start the server
port = 8001
if len(sys.argv) > 1:
    port = sys.argv[1]

# Run uvicorn
subprocess.run([
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv/bin/uvicorn"),
    "src.main:app",
    "--reload",
    "--port", str(port)
])
