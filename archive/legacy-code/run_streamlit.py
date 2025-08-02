#!/usr/bin/env python3
"""
Script to run Streamlit app with the correct Python interpreter
"""
import sys
import subprocess
import os

# Get the current Python executable
current_python = sys.executable
print(f"Using Python from: {current_python}")

# Run streamlit with the current Python interpreter
try:
    subprocess.run([current_python, "-m", "streamlit", "run", "examsoft_formatter_updated.py"], check=True)
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Streamlit might not be installed. Try installing it with:")
    print(f"{current_python} -m pip install streamlit")
except subprocess.CalledProcessError as e:
    print(f"Error running Streamlit: {e}")
