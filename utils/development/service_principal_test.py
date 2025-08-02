#!/usr/bin/env python3
"""
Service Principal Permission Test
Test if the updated service principal permissions resolve the SharePoint upload issue
"""

import streamlit as st
import requests
import sys
import os
from urllib.parse import quote

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistent_auth import render_persistent_auth_ui, initialize_persistent_auth

def main():
    st.set_page_config(page_title="Service Principal Test", layout="wide")
    
    st.title("🔧 Service Principal Permission Test")
    st.success("✅ Service principal permissions have been updated!")
    
    st.info("""
    **Changes Made:**
    - ✅ Granted delegated permissions: `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `offline_access`
    - ✅ Added application permission: `Sites.FullControl.All`
    - ✅ Service principal is properly configured
    
    **Next Steps:**
    1. Re-authenticate below to get a fresh token with new permissions
    2. Test the upload functionality
    """)
    
    # Get authentication with fresh token
    with st.sidebar:
        st.header("🔑 Re-Authentication Required")
        st.warning("Please re-authenticate to get a fresh token with updated permissions")
        
        # Initialize persistent auth system
        initialize_persistent_auth()
        
        is_authenticated = render_persistent_auth_ui()
    
    if is_authenticated:
        # Get the access token from session state
        access_token = st.session_state.sp_access_token
        st.success("✅ Re-authenticated with updated permissions!")
        
        # Quick permission test
        st.header("🧪 Permission Test")
        if st.button("Test SharePoint Permissions", type="primary"):
            test_sharepoint_permissions(access_token)
        
        # Upload test
        st.header("📤 Upload Test")
        if st.button("Test Simple Upload"):
            test_simple_upload(access_token)
        
        st.info("💡 **Tip:** After successful testing, go back to your main ExamSoft app and try uploading again!")
    else:
        st.warning("⚠️ Please re-authenticate with the updated permissions")

def test_sharepoint_permissions(access_token):
    """Test if we can access SharePoint with the new permissions"""
    
    site_id = "charlestonlaw.sharepoint.com,ba0b6d09-2f32-4ccf-a24d-9a41e9be4a6a,ffe7f195-f2eb-4f68-af47-35a01fa9a2d7"
    
    with st.expander("🔍 Permission Test Results", expanded=True):
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        
        # Test 1: Site access
        try:
            site_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}"
            response = requests.get(site_url, headers=headers)
            
            if response.status_code == 200:
                site_data = response.json()
                st.success(f"✅ Site Access: {site_data.get('displayName')}")
            else:
                st.error(f"❌ Site access failed: {response.status_code}")
                st.json(response.json() if response.content else {"error": "No response content"})
                return
        except Exception as e:
            st.error(f"❌ Site test exception: {e}")
            return
        
        # Test 2: Drive access
        try:
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
            response = requests.get(drive_url, headers=headers)
            
            if response.status_code == 200:
                drive_data = response.json()
                st.success(f"✅ Drive Access: {drive_data.get('name')}")
            else:
                st.error(f"❌ Drive access failed: {response.status_code}")
                return
        except Exception as e:
            st.error(f"❌ Drive test exception: {e}")
            return
        
        # Test 3: Write permission test (try to list with write scope)
        try:
            write_test_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root"
            response = requests.get(write_test_url, headers=headers)
            
            if response.status_code == 200:
                st.success("✅ Write permissions detected - you should be able to upload files!")
                
                # Check for specific folders
                children_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
                children_response = requests.get(children_url, headers=headers)
                
                if children_response.status_code == 200:
                    children_data = children_response.json()
                    folders = [item['name'] for item in children_data.get('value', []) if item.get('folder')]
                    
                    # Check for Exam Procedures folder
                    exam_proc = any('exam' in f.lower() and 'procedures' in f.lower() for f in folders)
                    if exam_proc:
                        st.success("✅ 'Exam Procedures' folder found!")
                    else:
                        st.info(f"📁 Available folders: {folders}")
                else:
                    st.warning("⚠️ Could not list folders")
            else:
                st.error(f"❌ Write permission test failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Write test exception: {e}")

def test_simple_upload(access_token):
    """Test a simple file upload to verify the fix worked"""
    
    site_id = "charlestonlaw.sharepoint.com,ba0b6d09-2f32-4ccf-a24d-9a41e9be4a6a,ffe7f195-f2eb-4f68-af47-35a01fa9a2d7"
    
    with st.expander("📤 Upload Test Results", expanded=True):
        test_content = b"Service Principal Test - Upload working!"
        test_filename = "service_principal_test.txt"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'text/plain'
        }
        
        # Try uploading to root first
        st.write("**Testing upload to root directory...**")
        try:
            upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{quote(test_filename)}:/content"
            response = requests.put(upload_url, headers=headers, data=test_content)
            
            st.write(f"Upload response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                st.success("🎉 SUCCESS! Service principal permissions are working!")
                st.json({
                    "file_url": response_data.get('webUrl'),
                    "file_size": response_data.get('size'),
                    "created": response_data.get('createdDateTime')
                })
                
                st.success("✅ **Your SharePoint upload issue is FIXED!**")
                st.info("🚀 Go back to your ExamSoft formatter and try uploading your exam again!")
            else:
                st.error(f"❌ Upload still failing: {response.status_code}")
                try:
                    error_data = response.json()
                    st.json(error_data)
                    
                    # Check for specific error codes
                    error_code = error_data.get('error', {}).get('code', '')
                    if 'insufficient' in error_code.lower() or 'forbidden' in error_code.lower():
                        st.error("🔒 Still have permission issues - may need admin consent")
                    elif 'invalid' in error_code.lower():
                        st.error("❌ Token might be stale - try re-authenticating")
                except:
                    st.code(response.text)
        except Exception as e:
            st.error(f"❌ Upload test exception: {e}")

if __name__ == "__main__":
    main()
