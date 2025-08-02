# SharePoint Integration Module for ExamSoft Formatter
# This module handles Microsoft 365 authentication and SharePoint file uploads

import streamlit as st
import msal
import requests
import json

# Import configuration
try:
    from examsoft_m365_config import M365_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    M365_CONFIG = {}

def get_msal_auth():
    """Get MSAL authentication app for device code flow"""
    if not CONFIG_AVAILABLE:
        return None
    
    # Force public client application for device code flow
    # Do not provide client_secret to avoid confidential client issues
    app = msal.PublicClientApplication(
        client_id=M365_CONFIG["client_id"],
        authority=M365_CONFIG["authority"],
        # Explicitly disable token caching to avoid conflicts
        token_cache=None
    )
    return app

def get_device_flow():
    """Initiate device code flow for authentication"""
    if not CONFIG_AVAILABLE:
        return None
    
    app = get_msal_auth()
    if app:
        flow = app.initiate_device_flow(scopes=M365_CONFIG["scope"])
        return flow
    return None

def complete_device_flow(flow):
    """Complete device code flow and get access token"""
    if not CONFIG_AVAILABLE:
        return None
    
    app = get_msal_auth()
    if app and flow:
        result = app.acquire_token_by_device_flow(flow)
        return result
    return None

def get_sharepoint_sites(access_token):
    """Get available SharePoint sites using Microsoft Graph API"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get sites
        sites_url = "https://graph.microsoft.com/v1.0/sites?search=*"
        response = requests.get(sites_url, headers=headers)
        
        if response.status_code == 200:
            sites_data = response.json()
            sites = []
            for site in sites_data.get('value', []):
                sites.append({
                    'id': site['id'],
                    'name': site['displayName'],
                    'url': site['webUrl']
                })
            return sites
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching sites: {str(e)}")
        return []

def get_site_id_from_url(site_url, access_token):
    """Extract site ID from SharePoint URL using Microsoft Graph API"""
    try:
        # Parse the URL to get the hostname and site path
        from urllib.parse import urlparse
        parsed_url = urlparse(site_url)
        hostname = parsed_url.netloc
        site_path = parsed_url.path
        
        # Remove leading/trailing slashes and get site name
        site_path = site_path.strip('/')
        if site_path.startswith('sites/'):
            site_name = site_path.split('/')[-1]
        else:
            site_name = site_path
        
        # Debug information
        st.write(f"🔍 **Debug Info:**")
        st.write(f"- Site URL: {site_url}")
        st.write(f"- Hostname: {hostname}")
        st.write(f"- Site Path: {site_path}")
        st.write(f"- Site Name: {site_name}")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get site information using Microsoft Graph API
        graph_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site_name}"
        st.write(f"- Graph API URL: {graph_url}")
        
        response = requests.get(graph_url, headers=headers)
        
        st.write(f"- API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            site_data = response.json()
            st.write(f"- Site ID: {site_data['id']}")
            st.write(f"- Site Display Name: {site_data.get('displayName', site_name)}")
            return site_data['id'], site_data.get('displayName', site_name)
        else:
            st.error(f"Could not find SharePoint site: {response.status_code} - {response.text}")
            st.write(f"**Error Details:** {response.text}")
            return None, None
            
    except Exception as e:
        st.error(f"Error parsing SharePoint URL: {str(e)}")
        return None, None

def get_default_drive_id(site_id, access_token):
    """Get the default document library drive ID for a SharePoint site"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get the default drive (usually 'Documents' library)
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
        st.write(f"- Drive API URL: {drive_url}")
        
        response = requests.get(drive_url, headers=headers)
        
        st.write(f"- Drive Response Status: {response.status_code}")
        
        if response.status_code == 200:
            drive_data = response.json()
            st.write(f"- Drive ID: {drive_data['id']}")
            st.write(f"- Drive Name: {drive_data.get('name', 'Unknown')}")
            return drive_data['id']
        else:
            st.error(f"Could not access site drive: {response.status_code} - {response.text}")
            st.write(f"**Drive Error Details:** {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error getting drive ID: {str(e)}")
        return None

def query_sharepoint_folder(site_id, drive_id, access_token, folder_path=""):
    """Query SharePoint folder contents to see what files are actually there"""
    try:
        from urllib.parse import quote
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Build the query path
        if folder_path:
            # Clean up folder path
            folder_path = folder_path.strip()
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path
            if folder_path.endswith('/'):
                folder_path = folder_path[:-1]
            
            # URL encode the folder path
            path_parts = folder_path.split('/')
            encoded_parts = [quote(part) if part else '' for part in path_parts]
            encoded_folder_path = '/'.join(encoded_parts)
            
            query_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{encoded_folder_path}:/children"
        else:
            query_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children"
        
        st.write(f"🔍 **Folder Query Debug:**")
        st.write(f"- Folder Path: {folder_path}")
        st.write(f"- Query URL: {query_url}")
        
        response = requests.get(query_url, headers=headers)
        st.write(f"- Query Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('value', [])
            st.write(f"- **Found {len(files)} items in folder**")
            
            if files:
                st.write("**📁 Folder Contents:**")
                for item in files:
                    name = item.get('name', 'Unknown')
                    size = item.get('size', 0)
                    created = item.get('createdDateTime', 'Unknown')
                    modified = item.get('lastModifiedDateTime', 'Unknown')
                    web_url = item.get('webUrl', 'No URL')
                    
                    st.write(f"  • **{name}** ({size} bytes)")
                    st.write(f"    - Created: {created}")
                    st.write(f"    - Modified: {modified}")
                    st.write(f"    - URL: {web_url}")
                    st.write("---")
            else:
                st.write("**Folder is empty or no files found**")
            
            return True, files
        else:
            st.write(f"**Query Error:** {response.text}")
            return False, f"Query failed: {response.status_code} - {response.text}"
            
    except Exception as e:
        st.write(f"**Query Exception:** {str(e)}")
        return False, f"SharePoint query error: {str(e)}"

def upload_to_sharepoint_oauth(file_content, filename, site_id, drive_id, access_token, folder_path=""):
    """Upload file to SharePoint using Microsoft Graph API with OAuth token"""
    try:
        from urllib.parse import quote
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        # Build the upload path with folder support
        if folder_path:
            # Clean up folder path - ensure it starts with / and doesn't end with /
            folder_path = folder_path.strip()
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path
            if folder_path.endswith('/'):
                folder_path = folder_path[:-1]
            
            # URL encode the folder path to handle spaces and special characters
            # Split by '/', encode each part, then rejoin
            path_parts = folder_path.split('/')
            encoded_parts = [quote(part) if part else '' for part in path_parts]
            encoded_folder_path = '/'.join(encoded_parts)
            
            upload_path = f"{encoded_folder_path}/{quote(filename)}"
        else:
            upload_path = f"/{quote(filename)}"
        
        # Microsoft Graph API endpoint for file upload with folder path
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{upload_path}:/content"
        
        # Debug information
        st.write(f"📤 **Upload Debug:**")
        st.write(f"- Filename: {filename}")
        st.write(f"- Original Folder Path: {folder_path}")
        st.write(f"- Encoded Folder Path: {encoded_folder_path if folder_path else 'root'}")
        st.write(f"- Upload Path: {upload_path}")
        st.write(f"- Upload URL: {upload_url}")
        st.write(f"- File Size: {len(file_content) if isinstance(file_content, (str, bytes)) else 'Unknown'} bytes")
        
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
        elif hasattr(file_content, 'read'):
            file_content = file_content.read()
        
        response = requests.put(upload_url, headers=headers, data=file_content)
        
        st.write(f"- Upload Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            st.write(f"- **File URL:** {file_url}")
            return True, f"Successfully uploaded {filename} to SharePoint folder: {folder_path if folder_path else 'root'}\n📎 Direct link: {file_url}"
        else:
            st.write(f"**Upload Error Details:** {response.text}")
            return False, f"Upload failed: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"SharePoint upload error: {str(e)}"

def render_sharepoint_ui(data):
    """Render the SharePoint upload UI in Streamlit"""
    st.markdown("---")
    st.subheader("📤 Upload to SharePoint (Optional)")
    
    # Check if MSAL is available
    try:
        import msal
        MSAL_AVAILABLE = True
    except ImportError:
        MSAL_AVAILABLE = False
    
    if MSAL_AVAILABLE and CONFIG_AVAILABLE:
        with st.expander("SharePoint Upload Settings", expanded=False):
            st.write("🔐 **Secure Microsoft 365 Authentication**")
            st.write("Sign in with your Charleston School of Law Microsoft 365 account to upload files securely.")
            
            # Show current configuration
            st.write("**Current Configuration:**")
            st.code(f"""
App Registration Details:
- Client ID: {M365_CONFIG['client_id']}
- Tenant: {M365_CONFIG['tenant_id']}
- Status: ✅ Configuration loaded successfully
            """)
            
            # Initialize session state variables
            if 'access_token' not in st.session_state:
                st.session_state.access_token = None
            if 'auth_step' not in st.session_state:
                st.session_state.auth_step = 'initial'
            if 'device_flow' not in st.session_state:
                st.session_state.device_flow = None
            
            if st.session_state.access_token is None:
                # Authentication section
                st.write("**Step 1: Authenticate with Microsoft 365**")
                
                if st.session_state.auth_step == 'initial':
                    if st.button("🔑 Sign in with Microsoft 365"):
                        device_flow = get_device_flow()
                        if device_flow:
                            st.session_state.device_flow = device_flow
                            st.session_state.auth_step = 'device_code'
                            st.rerun()
                        else:
                            st.error("❌ Could not initiate authentication. Check configuration.")
                
                elif st.session_state.auth_step == 'device_code':
                    if st.session_state.device_flow:
                        st.success("✅ Authentication code generated!")
                        st.write("**Please follow these steps:**")
                        st.write("1. Go to the following URL in any browser:")
                        st.code(st.session_state.device_flow['verification_uri'])
                        st.write("2. Enter this code when prompted:")
                        st.code(st.session_state.device_flow['user_code'])
                        st.write("3. Sign in with your Charleston School of Law account")
                        st.write("4. Click the button below to complete authentication")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ I've completed the authentication"):
                                with st.spinner("Completing authentication..."):
                                    result = complete_device_flow(st.session_state.device_flow)
                                    if result and 'access_token' in result:
                                        st.session_state.access_token = result['access_token']
                                        st.session_state.auth_step = 'authenticated'
                                        st.session_state.device_flow = None
                                        st.success("🎉 Successfully authenticated!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Authentication not complete yet or failed. Please try again.")
                                        if result and 'error' in result:
                                            st.error(f"Error: {result.get('error_description', result['error'])}")
                                        # Clear session state to force fresh authentication
                                        st.session_state.auth_step = 'initial'
                                        st.session_state.device_flow = None
                                        if 'access_token' in st.session_state:
                                            del st.session_state.access_token
                        
                        with col2:
                            if st.button("🔄 Start Over"):
                                st.session_state.auth_step = 'initial'
                                st.session_state.device_flow = None
                                st.rerun()
            else:
                st.success("✅ Authenticated with Microsoft 365")
                
                # SharePoint site selection with pre-configured Academic Affairs settings
                st.write("**Step 2: Select SharePoint Destination**")
                
                sharepoint_site_url = st.text_input(
                    "SharePoint Site URL:",
                    value="https://charlestonlaw.sharepoint.com/sites/acad_affairs",
                    help="Enter the URL of your SharePoint site where you want to upload files"
                )
                
                folder_path = st.text_input(
                    "Folder Path:",
                    value="Exam Procedures/ExamSoft/Import",
                    help="Enter the folder path within the SharePoint site (e.g., 'Exam Procedures/ExamSoft/Import')"
                )
                
                # Upload file selection
                st.write("**Step 3: Select Files to Upload**")
                upload_files = []
                
                if data.get('instructions_docx'):
                    upload_instructions_sp = st.checkbox("📄 Upload Instructions (DOCX) to SharePoint", value=True)
                    if upload_instructions_sp:
                        upload_files.append(('instructions', data['instructions_docx'], data['instructions_filename']))
                
                upload_exam_sp = st.checkbox("📝 Upload Exam (RTF) to SharePoint", value=True)
                if upload_exam_sp:
                    exam_content = data.get('exam_rtf_bytes') or data.get('exam_rtf_content')
                    if exam_content:
                        upload_files.append(('exam', exam_content, data['exam_filename']))
                
                # Upload button
                if upload_files and sharepoint_site_url:
                    st.write(f"**Ready to upload {len(upload_files)} file(s) to:**")
                    st.write(f"📍 {sharepoint_site_url}/{folder_path}")
                    
                    # Add folder query button for debugging
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔍 Query Folder Contents", help="Check what files are currently in the SharePoint folder"):
                            status_placeholder = st.empty()
                            status_placeholder.write("🔍 Getting SharePoint site information...")
                            
                            site_id, site_name = get_site_id_from_url(sharepoint_site_url, st.session_state.access_token)
                            if site_id:
                                status_placeholder.write("🔍 Getting drive information...")
                                drive_id = get_default_drive_id(site_id, st.session_state.access_token)
                                
                                if drive_id:
                                    status_placeholder.write("� Querying folder contents...")
                                    success, files = query_sharepoint_folder(
                                        site_id,
                                        drive_id, 
                                        st.session_state.access_token,
                                        folder_path
                                    )
                                    if success:
                                        status_placeholder.success(f"✅ Successfully queried folder: {folder_path}")
                                    else:
                                        status_placeholder.error(f"❌ Failed to query folder: {files}")
                                else:
                                    status_placeholder.error("❌ Could not get drive information")
                            else:
                                status_placeholder.error("❌ Could not get site information")
                    
                    with col2:
                        if st.button("�🚀 Upload to SharePoint", use_container_width=True):
                            upload_progress = st.progress(0)
                            status_placeholder = st.empty()
                            
                            # Get site ID and drive ID
                            status_placeholder.write("🔍 Getting SharePoint site information...")
                            site_id, site_name = get_site_id_from_url(sharepoint_site_url, st.session_state.access_token)
                        
                        if not site_id:
                            st.error("❌ Could not access SharePoint site. Please check the URL and permissions.")
                            return
                        
                        drive_id = get_default_drive_id(site_id, st.session_state.access_token)
                        if not drive_id:
                            st.error("❌ Could not access SharePoint document library.")
                            return
                        
                        success_count = 0
                        total_files = len(upload_files)
                        
                        for i, (file_type, content, filename) in enumerate(upload_files):
                            progress = (i + 1) / total_files
                            upload_progress.progress(progress)
                            status_placeholder.write(f"📤 Uploading {filename}...")
                            
                            try:
                                # Upload to SharePoint using the real API
                                success, message = upload_to_sharepoint_oauth(
                                    content, 
                                    filename, 
                                    site_id, 
                                    drive_id, 
                                    st.session_state.access_token,
                                    folder_path
                                )
                                
                                if success:
                                    status_placeholder.success(f"✅ {message}")
                                    success_count += 1
                                else:
                                    status_placeholder.error(f"❌ {message}")
                                
                            except Exception as e:
                                status_placeholder.error(f"❌ Failed to upload {filename}: {str(e)}")
                        
                        upload_progress.progress(1.0)
                        
                        if success_count > 0:
                            st.balloons()
                            st.success(f"🎉 Successfully uploaded {success_count} of {total_files} file(s) to SharePoint!")
                            
                            # Auto-query folder after successful uploads to verify
                            st.write("**🔍 Verifying uploaded files in SharePoint folder:**")
                            success, files = query_sharepoint_folder(
                                site_id,
                                drive_id, 
                                st.session_state.access_token,
                                folder_path
                            )
                            if success:
                                st.info("✅ Folder verification complete - see details above")
                            else:
                                st.warning("⚠️ Could not verify folder contents after upload")
                        
                        if success_count < total_files:
                            st.warning(f"⚠️ {total_files - success_count} file(s) failed to upload. Please try again.")
                
                elif upload_files and not sharepoint_site_url:
                    st.info("📍 Please enter your SharePoint site URL to proceed with upload.")
                
                elif not upload_files:
                    st.info("📋 Please select at least one file to upload.")
                
                # Sign out button
                st.write("---")
                if st.button("🔓 Sign Out"):
                    st.session_state.access_token = None
                    st.success("👋 Successfully signed out!")
                    st.rerun()
                    
    elif MSAL_AVAILABLE and not CONFIG_AVAILABLE:
        st.info("📋 **Configuration Required**: Microsoft 365 app registration configuration not found.")
        st.write("The `examsoft_m365_config.py` file is required for SharePoint integration.")
        st.write("**Next Steps:**")
        st.write("1. Ensure the config file exists in your project directory")
        st.write("2. Verify it contains the correct client_id and client_secret")
        st.write("3. Restart the Streamlit application")
        
    else:
        st.warning("⚠️ SharePoint functionality not available.")
        st.write("**Required packages missing. Please install:**")
        st.code("pip install msal")
        st.write("Then restart the application.")
