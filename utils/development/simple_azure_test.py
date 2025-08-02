#!/usr/bin/env python3
"""Simple test for Azure configuration without Streamlit"""

import os
import json

def simple_test():
    print("Testing Azure Configuration...")
    print("=" * 40)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check if file exists
    config_file = 'azure_config.json'
    if os.path.exists(config_file):
        print(f"✅ Found {config_file}")
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"Configuration: {config}")
        
        endpoint = config.get('azure_endpoint', 'Not found')
        print(f"Azure endpoint: {endpoint}")
        
        if endpoint and endpoint != 'Not found':
            print("✅ Azure configuration is valid!")
            return True
    else:
        print(f"❌ {config_file} not found")
        print(f"Files in directory: {os.listdir('.')}")
    
    return False

if __name__ == "__main__":
    simple_test()
