#!/usr/bin/env python3
"""
Quick SharePoint Upload Test
This will use your existing authentication to test uploads step by step
"""

import streamlit as st
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from persistent_auth import render_persistent_auth_ui

def main():
    st.set_page_config(page_title="SharePoint Upload Test", layout="wide")
    
    st.title("🧪 SharePoint Upload Test")
    st.write("This will test your SharePoint upload step by step")
    
    # Get authentication
    with st.sidebar:
        st.header("Authentication")
        auth_result = render_persistent_auth_ui()
    
    if auth_result['authenticated']:
        access_token = auth_result['access_token']
        st.success("✅ Authenticated successfully!")
        
        # Test 1: Basic API connectivity
        st.header("🔍 Test 1: Basic API Connectivity")
        if st.button("Test SharePoint Access"):
            test_basic_access(access_token)
        
        # Test 2: Simple file upload
        st.header("📤 Test 2: Simple File Upload")
        if st.button("Test Simple Upload"):
            test_simple_upload(access_token)
        
        # Test 3: Your RTF file
        st.header("📄 Test 3: RTF File Upload")
        if st.button("Test RTF Upload"):
            test_rtf_upload(access_token)
    else:
        st.warning("⚠️ Please authenticate first")

def test_basic_access(access_token):
    """Test basic SharePoint access"""
    import requests
    
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    with st.expander("🔍 Basic Access Test Results", expanded=True):
        # Test site access
        st.write("**Testing site access...**")
        try:
            site_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}"
            headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
            response = requests.get(site_url, headers=headers)
            
            if response.status_code == 200:
                site_data = response.json()
                st.success(f"✅ Site accessible: {site_data.get('displayName', 'Unknown')}")
                st.json({"site_name": site_data.get('displayName'), "web_url": site_data.get('webUrl')})
            else:
                st.error(f"❌ Site access failed: {response.status_code}")
                st.code(response.text)
                return
        except Exception as e:
            st.error(f"❌ Exception: {e}")
            return
        
        # Test drive access
        st.write("**Testing drive access...**")
        try:
            drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
            response = requests.get(drive_url, headers=headers)
            
            if response.status_code == 200:
                drive_data = response.json()
                st.success(f"✅ Drive accessible: {drive_data.get('name', 'Unknown')}")
                st.json({"drive_id": drive_data.get('id'), "drive_type": drive_data.get('driveType')})
            else:
                st.error(f"❌ Drive access failed: {response.status_code}")
                st.code(response.text)
                return
        except Exception as e:
            st.error(f"❌ Exception: {e}")
            return
        
        # Test root folder listing
        st.write("**Testing root folder listing...**")
        try:
            children_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
            response = requests.get(children_url, headers=headers)
            
            if response.status_code == 200:
                children_data = response.json()
                folders = [item['name'] for item in children_data.get('value', []) if item.get('folder')]
                files = [item['name'] for item in children_data.get('value', []) if not item.get('folder')]
                
                st.success("✅ Root folder accessible")
                st.write(f"**Folders found:** {folders}")
                st.write(f"**Files found:** {len(files)} files")
                
                # Check for Exam Procedures folder
                exam_procedures_found = any('exam' in folder.lower() and 'procedures' in folder.lower() for folder in folders)
                if exam_procedures_found:
                    st.success("✅ 'Exam Procedures' folder found!")
                else:
                    st.warning("⚠️ 'Exam Procedures' folder not found in root")
                    st.info("Available folders: " + ", ".join(folders))
            else:
                st.error(f"❌ Root folder access failed: {response.status_code}")
                st.code(response.text)
        except Exception as e:
            st.error(f"❌ Exception: {e}")

def test_simple_upload(access_token):
    """Test uploading a simple text file"""
    import requests
    
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    with st.expander("📤 Simple Upload Test Results", expanded=True):
        test_content = b"Hello from ExamSoft Formatter! This is a test file."
        test_filename = "test_upload.txt"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'text/plain'
        }
        
        # Try the simplest possible upload to root
        st.write("**Testing upload to root directory...**")
        try:
            upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{test_filename}:/content"
            st.code(upload_url)
            
            response = requests.put(upload_url, headers=headers, data=test_content)
            st.write(f"Response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                st.success("✅ Simple upload successful!")
                st.json({
                    "file_url": response_data.get('webUrl'),
                    "file_size": response_data.get('size'),
                    "created": response_data.get('createdDateTime')
                })
            else:
                st.error(f"❌ Upload failed: {response.status_code}")
                try:
                    error_data = response.json()
                    st.json(error_data)
                except:
                    st.code(response.text)
        except Exception as e:
            st.error(f"❌ Exception: {e}")

def test_rtf_upload(access_token):
    """Test uploading an RTF file like the exam"""
    import requests
    from urllib.parse import quote
    
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    with st.expander("📄 RTF Upload Test Results", expanded=True):
        # Create a simple RTF content
        rtf_content = r'''{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24 This is a test RTF file for ExamSoft formatting.
\par
Question 1. What is the capital of France?
\par
A. London
\par
B. Berlin  
\par
C. Paris
\par
D. Madrid
\par
}'''.encode('utf-8')
        
        test_filename = "test_exam.rtf"
        
        # Try different upload approaches
        upload_tests = [
            {
                'name': 'Root directory upload',
                'url': f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{quote(test_filename)}:/content",
                'content_type': 'application/rtf'
            },
            {
                'name': 'Root directory (octet-stream)',
                'url': f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{quote(test_filename)}:/content",
                'content_type': 'application/octet-stream'
            },
            {
                'name': 'Children API',
                'url': f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children",
                'content_type': 'multipart/form-data',
                'method': 'POST'
            }
        ]
        
        for test in upload_tests:
            st.write(f"**{test['name']}**")
            
            try:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': test['content_type']
                }
                
                if test.get('method') == 'POST':
                    # Use multipart upload for children API
                    files = {'file': (test_filename, rtf_content, 'application/rtf')}
                    response = requests.post(test['url'], headers={'Authorization': f'Bearer {access_token}'}, files=files)
                else:
                    # Use PUT for content upload
                    response = requests.put(test['url'], headers=headers, data=rtf_content)
                
                st.write(f"Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    st.success(f"✅ {test['name']} successful!")
                    st.json({
                        "file_url": response_data.get('webUrl'),
                        "file_size": response_data.get('size')
                    })
                    break  # Success! Stop testing
                else:
                    st.error(f"❌ Failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        st.json(error_data)
                    except:
                        st.code(response.text[:500])
            except Exception as e:
                st.error(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
