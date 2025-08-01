#!/usr/bin/env python3
"""
Diagnostic tool to test Microsoft 365 authentication configuration
This helps identify exactly what's wrong with the current setup
"""

import streamlit as st
import sys
import traceback

def test_msal_import():
    """Test if MSAL library is available"""
    try:
        import msal
        return True, f"MSAL version: {msal.__version__}"
    except ImportError as e:
        return False, f"MSAL import failed: {e}"

def test_config_loading():
    """Test if M365 configuration loads properly"""
    try:
        from examsoft_m365_config import M365_CONFIG, APP_REGISTRATION_INFO
        
        required_keys = ['client_id', 'tenant_id', 'authority', 'scope', 'redirect_uri']
        missing_keys = [key for key in required_keys if not M365_CONFIG.get(key)]
        
        if missing_keys:
            return False, f"Missing config keys: {missing_keys}"
        
        return True, {
            'client_id': M365_CONFIG['client_id'][:8] + '...',
            'authority': M365_CONFIG['authority'],
            'redirect_uri': M365_CONFIG['redirect_uri'],
            'scopes': len(M365_CONFIG['scope']),
            'app_info': APP_REGISTRATION_INFO
        }
    except Exception as e:
        return False, f"Config loading failed: {e}"

def test_device_flow_creation():
    """Test if device flow can be created"""
    try:
        import msal
        from examsoft_m365_config import M365_CONFIG
        
        app = msal.PublicClientApplication(
            M365_CONFIG['client_id'],
            authority=M365_CONFIG['authority']
        )
        
        flow = app.initiate_device_flow(scopes=M365_CONFIG['scope'])
        
        if "user_code" not in flow:
            return False, f"Device flow failed: {flow.get('error_description', 'Unknown error')}"
        
        return True, {
            'verification_uri': flow.get('verification_uri'),
            'user_code': flow.get('user_code')[:4] + '...',
            'expires_in': flow.get('expires_in'),
            'message': flow.get('message', '')[:100] + '...'
        }
    except Exception as e:
        return False, f"Device flow creation failed: {e}"

def main():
    """Run all diagnostic tests"""
    print("🔍 **MICROSOFT 365 AUTHENTICATION DIAGNOSTICS**")
    print("=" * 55)
    print()
    
    # Test 1: MSAL Import
    print("1. **Testing MSAL Library Import...**")
    success, result = test_msal_import()
    if success:
        print(f"   ✅ {result}")
    else:
        print(f"   ❌ {result}")
        return
    print()
    
    # Test 2: Configuration Loading
    print("2. **Testing Configuration Loading...**")
    success, result = test_config_loading()
    if success:
        print("   ✅ Configuration loaded successfully:")
        for key, value in result.items():
            if key == 'app_info':
                print(f"      {key}: App registration found")
            else:
                print(f"      {key}: {value}")
    else:
        print(f"   ❌ {result}")
        return
    print()
    
    # Test 3: Device Flow Creation
    print("3. **Testing Device Flow Creation...**")
    success, result = test_device_flow_creation()
    if success:
        print("   ✅ Device flow created successfully:")
        for key, value in result.items():
            print(f"      {key}: {value}")
        print()
        print("   🎉 **Authentication should work!**")
        print("   The issue might be in the Streamlit UI flow, not the Azure configuration.")
    else:
        print(f"   ❌ {result}")
        print()
        print("   🔧 **This indicates an Azure AD app registration issue.**")
        print("   Please run: python update_app_registration_for_streamlit_cloud.py")
        print("   And follow the instructions to fix the app registration.")
    print()
    
    print("📋 **SUMMARY:**")
    if success:
        print("✅ All tests passed - Azure configuration appears correct")
        print("❓ If authentication still fails, the issue is likely in the Streamlit UI flow")
    else:
        print("❌ Tests failed - Azure AD app registration needs to be updated")
        print("🔧 Run the update script and follow Azure Portal instructions")
    print()

if __name__ == "__main__":
    main()
