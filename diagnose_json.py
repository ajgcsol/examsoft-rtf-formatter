#!/usr/bin/env python3
"""Diagnose JSON file issues"""

import os

def diagnose_json_file():
    filename = 'azure_config.json'
    
    print(f"Diagnosing {filename}...")
    print("=" * 40)
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ File {filename} does not exist")
        return
    
    # Check file size
    size = os.path.getsize(filename)
    print(f"File size: {size} bytes")
    
    # Read raw bytes
    with open(filename, 'rb') as f:
        raw_bytes = f.read()
    
    print(f"First 20 bytes (hex): {raw_bytes[:20].hex()}")
    print(f"First 20 bytes (repr): {repr(raw_bytes[:20])}")
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'ascii']
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ Successfully read with {encoding}: {len(content)} chars")
            print(f"First 50 chars: {repr(content[:50])}")
            
            # Try parsing as JSON
            import json
            try:
                data = json.loads(content)
                print(f"✅ Valid JSON with {encoding}")
                print(f"Keys: {list(data.keys())}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse failed with {encoding}: {e}")
                
        except UnicodeDecodeError as e:
            print(f"❌ Failed to read with {encoding}: {e}")
    
    return False

if __name__ == "__main__":
    diagnose_json_file()
