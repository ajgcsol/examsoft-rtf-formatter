# ExamSoft Formatter - Microsoft 365 Configuration
# Supports both local development and Streamlit Cloud deployment

import streamlit as st

# Debug configuration loading
print("🔍 Loading M365 configuration...")

# Try to get config from Streamlit secrets first (for cloud deployment)
try:
    # Check if we're running in Streamlit Cloud
    has_secrets = hasattr(st, 'secrets') and len(st.secrets) > 0
    print(f"🔍 Has secrets: {has_secrets}")
    
    if has_secrets:
        print("🔍 Using Streamlit Cloud secrets...")
        M365_CONFIG = {
            "client_id": st.secrets.get("M365", {}).get("M365_CLIENT_ID", "4848a7e9-327a-49ff-a789-6f8b928615b7"),
            "tenant_id": st.secrets.get("M365", {}).get("M365_TENANT_ID", "charlestonlaw.edu"), 
            "authority": st.secrets.get("M365", {}).get("M365_AUTHORITY", "https://login.microsoftonline.com/charlestonlaw.edu"),
            "scope": [
                "https://graph.microsoft.com/Sites.ReadWrite.All", 
                "https://graph.microsoft.com/Files.ReadWrite.All",
                "https://graph.microsoft.com/User.Read"
            ],
            "redirect_uri": "https://csol-examsoft-converter.streamlit.app"
        }
        print(f"🔍 Cloud config loaded - Client ID: {M365_CONFIG['client_id'][:8]}...")
    else:
        raise Exception("No secrets found, using fallback")
        
except Exception as e:
    print(f"🔍 Exception loading cloud config: {e}")
    # Fallback for local development
    print("🔍 Using local development fallback...")
    M365_CONFIG = {
        "client_id": "4848a7e9-327a-49ff-a789-6f8b928615b7",
        "tenant_id": "charlestonlaw.edu",
        "authority": "https://login.microsoftonline.com/charlestonlaw.edu",
        "scope": [
            "https://graph.microsoft.com/Sites.ReadWrite.All", 
            "https://graph.microsoft.com/Files.ReadWrite.All",
            "https://graph.microsoft.com/User.Read"
        ],
        "redirect_uri": "http://localhost:8501"
    }
    print(f"🔍 Local config loaded - Client ID: {M365_CONFIG['client_id'][:8]}...")

# Azure AD App Registration Details
APP_REGISTRATION_INFO = {
    "app_name": "ExamSoft Formatter",
    "app_id": "4848a7e9-327a-49ff-a789-6f8b928615b7", 
    "object_id": "20d20db1-5ad9-49aa-a372-7102f92bd94d",
    "tenant_id": "40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078",
    "service_principal_id": "",
    "created_date": "2025-08-01T00:14:15Z"
}
