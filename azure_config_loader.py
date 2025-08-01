# Azure Configuration Loader for ExamSoft Formatter
# This module loads Azure configuration and provides Azure-aware functions

import os
import requests
import streamlit as st

# Default configuration
DEFAULT_CONFIG = {
    'AZURE_CONVERTER_ENDPOINT': 'http://localhost:8080/convert',
    'AZURE_RESOURCE_GROUP': None,
    'AZURE_ACI_NAME': None,
    'AZURE_ACR_NAME': None,
    'USE_AZURE': False
}

def load_azure_config():
    """Load Azure configuration from azure_config.json file or environment variables"""
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from azure_config.json file (created by deployment script)
    try:
        import json
        
        # Try multiple possible locations for the config file
        config_paths = [
            'azure_config.json',
            os.path.join(os.path.dirname(__file__), 'azure_config.json'),
            os.path.abspath('azure_config.json')
        ]
        
        azure_config = None
        config_path_used = None
        
        for config_path in config_paths:
            try:
                # Try with utf-8-sig first to handle BOM, then fallback to utf-8
                for encoding in ['utf-8-sig', 'utf-8']:
                    try:
                        with open(config_path, 'r', encoding=encoding) as f:
                            azure_config = json.load(f)
                            config_path_used = config_path
                            break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                if azure_config:
                    break
            except FileNotFoundError:
                continue
        
        if azure_config:
            # Update config with values from JSON file
            if 'azure_endpoint' in azure_config:
                # Convert from azure_endpoint to AZURE_CONVERTER_ENDPOINT format
                endpoint = azure_config['azure_endpoint']
                if not endpoint.endswith('/convert'):
                    endpoint = endpoint + '/convert'
                config['AZURE_CONVERTER_ENDPOINT'] = endpoint
                config['USE_AZURE'] = True
            
            if 'resource_group' in azure_config:
                config['AZURE_RESOURCE_GROUP'] = azure_config['resource_group']
            if 'container_name' in azure_config:
                config['AZURE_ACI_NAME'] = azure_config['container_name']
            if 'acr_name' in azure_config:
                config['AZURE_ACR_NAME'] = azure_config['acr_name']
                    
            print(f"Azure configuration loaded from {config_path_used}")
        else:
            raise FileNotFoundError("azure_config.json not found in any expected location")
            
    except (FileNotFoundError, ImportError, AttributeError, json.JSONDecodeError) as e:
        pass  # Silent fallback to defaults
    
    # Override with environment variables if they exist
    env_endpoint = os.getenv('AZURE_CONVERTER_ENDPOINT')
    if env_endpoint:
        config['AZURE_CONVERTER_ENDPOINT'] = env_endpoint
        config['USE_AZURE'] = True
    
    config['AZURE_RESOURCE_GROUP'] = os.getenv('AZURE_RESOURCE_GROUP', config['AZURE_RESOURCE_GROUP'])
    config['AZURE_ACI_NAME'] = os.getenv('AZURE_ACI_NAME', config['AZURE_ACI_NAME'])
    config['AZURE_ACR_NAME'] = os.getenv('AZURE_ACR_NAME', config['AZURE_ACR_NAME'])
    
    return config

def get_converter_endpoint():
    """Get the converter endpoint (Azure or local)"""
    config = load_azure_config()
    return config['AZURE_CONVERTER_ENDPOINT']

def is_using_azure():
    """Check if we're using Azure endpoints"""
    config = load_azure_config()
    return config['USE_AZURE']

def test_converter_endpoint(endpoint_url):
    """Test if the converter endpoint is available"""
    try:
        # Test with a simple GET request to the base URL (remove /convert)
        base_url = endpoint_url.replace('/convert', '')
        response = requests.get(base_url, timeout=10)
        return True, f"Endpoint responding with status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Endpoint unavailable: {str(e)}"

def show_azure_status():
    """Display Azure configuration status in Streamlit"""
    config = load_azure_config()
    
    if config['USE_AZURE']:
        st.success("🌤️ **Using Azure Cloud Endpoint** - LibreOffice conversion service deployed")
        
        # Show just the essential info by default
        col1, col2 = st.columns([3, 1])
        with col1:
            endpoint_clean = config['AZURE_CONVERTER_ENDPOINT'].replace('/convert', '')
            st.write(f"📍 **Endpoint**: `{endpoint_clean}`")
        with col2:
            # Quick health check button
            if st.button("🔍 Test", help="Test Azure endpoint"):
                with st.spinner("Testing..."):
                    is_available, message = test_converter_endpoint(config['AZURE_CONVERTER_ENDPOINT'])
                    if is_available:
                        st.success("✅ Online")
                    else:
                        st.error("❌ Offline")
    else:
        st.info("🏠 **Using Local Docker Endpoint** - Deploy to Azure for cloud conversion service")

def get_azure_monitoring_commands():
    """Get Azure CLI commands for monitoring the deployment"""
    config = load_azure_config()
    
    if not config['USE_AZURE'] or not all([config['AZURE_RESOURCE_GROUP'], config['AZURE_ACI_NAME']]):
        return None
    
    commands = {
        'logs': f"az container logs --name {config['AZURE_ACI_NAME']} --resource-group {config['AZURE_RESOURCE_GROUP']}",
        'status': f"az container show --name {config['AZURE_ACI_NAME']} --resource-group {config['AZURE_RESOURCE_GROUP']} --query 'instanceView.state' -o tsv",
        'restart': f"az container restart --name {config['AZURE_ACI_NAME']} --resource-group {config['AZURE_RESOURCE_GROUP']}",
        'delete': f"az container delete --name {config['AZURE_ACI_NAME']} --resource-group {config['AZURE_RESOURCE_GROUP']} --yes"
    }
    
    return commands
