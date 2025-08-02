import streamlit as st
import requests
try:
    import msal
    from examsoft_m365_config import M365_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    M365_CONFIG = {}

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 bytes"
    elif size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def format_path_readable(path):
    """Format SharePoint path in a more readable way"""
    if not path:
        return "(root)"
    # Remove the drive prefix and decode URL encoding
    clean_path = path.replace("/root:", "").replace("%20", " ")
    return clean_path if clean_path else "(root)"

def initialize_auth_session():
    """Initialize authentication session state variables"""
    # Use consistent session state keys for compatibility
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'sharepoint_access_token' not in st.session_state:
        st.session_state.sharepoint_access_token = None
    if 'sp_access_token' not in st.session_state:
        st.session_state.sp_access_token = None
    if 'sp_authenticated' not in st.session_state:
        st.session_state.sp_authenticated = False
    if 'sp_user_info' not in st.session_state:
        st.session_state.sp_user_info = None

def get_device_flow():
    """Start device code flow for authentication"""
    try:
        app = msal.PublicClientApplication(
            M365_CONFIG['client_id'],
            authority=M365_CONFIG['authority']
        )
        
        flow = app.initiate_device_flow(scopes=M365_CONFIG['scope'])
        if "user_code" not in flow:
            raise ValueError(f"Failed to create device flow: {flow.get('error_description', 'Unknown error')}")
        
        return app, flow
    except Exception as e:
        st.error(f"Failed to start authentication: {str(e)}")
        return None, None

def complete_device_flow(app, flow):
    """Complete device code flow and get access token"""
    try:
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            return result["access_token"], result.get("account")
        else:
            error_msg = result.get("error_description", "Unknown error")
            st.error(f"Authentication failed: {error_msg}")
            return None, None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None, None

def get_user_info(access_token):
    """Get user information from Microsoft Graph"""
    try:
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_site_id_from_url(site_url, access_token):
    """Extract site ID from SharePoint site URL"""
    try:
        from urllib.parse import urlparse
        
        parsed_url = urlparse(site_url)
        hostname = parsed_url.hostname
        site_path = parsed_url.path
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # For the acad_affairs site, the API URL should be specific
        if 'acad_affairs' in site_url:
            site_api_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/acad_affairs"
        elif site_path and site_path != '/':
            site_api_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}"
        else:
            site_api_url = f"https://graph.microsoft.com/v1.0/sites/{hostname}"
        
        response = requests.get(site_api_url, headers=headers)
        
        if response.status_code == 200:
            site_data = response.json()
            return site_data['id'], site_data.get('displayName', 'Unknown')
        else:
            return None, f"Could not access site: {response.status_code}"
    except Exception as e:
        return None, f"Site access error: {str(e)}"

def get_default_drive_id(site_id, access_token):
    """Get the default document library drive ID for the site"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives", headers=headers)
        
        if response.status_code == 200:
            drives = response.json().get('value', [])
            # Find the default document library (usually "Documents")
            for drive in drives:
                if drive.get('name') == 'Documents':
                    return drive['id']
            # If no "Documents" drive, use the first one
            if drives:
                return drives[0]['id']
        return None
    except Exception as e:
        return None

def upload_to_sharepoint_clean(file_content, filename, site_id, drive_id, access_token, folder_path=""):
    """Upload file to SharePoint with minimal debug output"""
    try:
        from urllib.parse import quote
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        # Build the upload path with folder support
        if folder_path:
            folder_path = folder_path.strip()
            if not folder_path.startswith('/'):
                folder_path = '/' + folder_path
            if folder_path.endswith('/'):
                folder_path = folder_path[:-1]
            
            path_parts = folder_path.split('/')
            
            # Fix for path duplication in Teams-enabled SharePoint sites
            if len(path_parts) >= 3 and path_parts[1] == "Exam Procedures" and path_parts[2] == "Exam Procedures":
                path_parts = [''] + path_parts[2:]  # Skip duplicate
            
            encoded_parts = [quote(part) if part else '' for part in path_parts]
            encoded_folder_path = '/'.join(encoded_parts)
            upload_path = f"{encoded_folder_path}/{quote(filename)}"
        else:
            upload_path = f"/{quote(filename)}"
        
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{upload_path}:/content"
        
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
        elif hasattr(file_content, 'read'):
            file_content = file_content.read()
        
        response = requests.put(upload_url, headers=headers, data=file_content)
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            file_size = response_data.get('size', len(file_content) if isinstance(file_content, bytes) else 0)
            
            return True, {
                'url': file_url,
                'size': file_size,
                'created': response_data.get('createdDateTime', 'N/A')
            }
        else:
            return False, f"Upload failed: {response.status_code}"
            
    except Exception as e:
        return False, f"Upload error: {str(e)}"

def render_auth_ui():
    """Render simplified authentication UI"""
    if not st.session_state.sp_authenticated:
        st.info("🔐 **Microsoft 365 Authentication Required**")
        st.write("Sign in to upload files to SharePoint")
        
        if 'auth_flow' not in st.session_state:
            if st.button("🔑 Sign in with Microsoft 365", use_container_width=True):
                with st.spinner("Starting authentication..."):
                    app, flow = get_device_flow()
                    if app and flow:
                        st.session_state.auth_app = app
                        st.session_state.auth_flow = flow
                        st.rerun()
        else:
            # Show device code
            col1, col2 = st.columns([2, 1])
            with col1:
                st.info(f"**Visit:** {st.session_state.auth_flow['verification_uri']}")
                st.code(st.session_state.auth_flow['user_code'], language=None)
            with col2:
                if st.button("✅ Complete Sign In", use_container_width=True):
                    with st.spinner("Completing authentication..."):
                        token, account = complete_device_flow(st.session_state.auth_app, st.session_state.auth_flow)
                        if token:
                            # Set all the session state keys for compatibility
                            st.session_state.sp_access_token = token
                            st.session_state.access_token = token
                            st.session_state.sharepoint_access_token = token
                            st.session_state.sp_authenticated = True
                            st.session_state.sp_user_info = get_user_info(token)
                            # Clear auth flow
                            if 'auth_flow' in st.session_state:
                                del st.session_state.auth_flow
                            if 'auth_app' in st.session_state:
                                del st.session_state.auth_app
                            st.success("🎉 Authentication successful!")
                            st.rerun()
                        else:
                            if 'auth_flow' in st.session_state:
                                del st.session_state.auth_flow
                            st.rerun()
        return False
    return True

def render_sharepoint_upload_ui(data):
    """Render simplified SharePoint upload UI"""
    st.markdown("---")
    st.subheader("📤 Upload to SharePoint")
    
    # Initialize session state
    initialize_auth_session()
    
    # Check if MSAL is available
    try:
        import msal
        MSAL_AVAILABLE = True
    except ImportError:
        MSAL_AVAILABLE = False
    
    if not MSAL_AVAILABLE:
        st.warning("⚠️ SharePoint functionality not available.")
        st.write("Please install required packages: `pip install msal`")
        return
    
    if not CONFIG_AVAILABLE:
        st.info("📋 **Configuration Required**: Microsoft 365 app registration not found.")
        return
    
    # Show user info if authenticated
    if st.session_state.sp_authenticated and st.session_state.sp_user_info:
        user_name = st.session_state.sp_user_info.get('displayName', 'Unknown User')
        user_email = st.session_state.sp_user_info.get('mail', st.session_state.sp_user_info.get('userPrincipalName', ''))
        st.success(f"✅ Signed in as: **{user_name}** ({user_email})")
    
    # Authentication flow - check multiple session state keys for compatibility
    is_authenticated = (st.session_state.sp_authenticated or 
                       bool(st.session_state.get('access_token')) or 
                       bool(st.session_state.get('sharepoint_access_token')))
    
    if not is_authenticated:
        return render_auth_ui()
    
    # Use the token - try different session state keys
    access_token = (st.session_state.sp_access_token or 
                   st.session_state.get('access_token') or 
                   st.session_state.get('sharepoint_access_token'))
    
    # Upload configuration
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            sharepoint_site_url = st.text_input(
                "SharePoint Site URL:",
                value="https://charlestonlaw.sharepoint.com/sites/acad_affairs",
                help="Enter your SharePoint site URL"
            )
            
            folder_path = st.text_input(
                "Folder Path:",
                value="Exam Procedures/ExamSoft/Import",
                help="Folder path within SharePoint"
            )
        
        with col2:
            st.write("**Files to Upload:**")
            upload_files = []
            
            if data.get('instructions_docx'):
                if st.checkbox("📄 Instructions (DOCX)", value=True):
                    upload_files.append(('instructions', data['instructions_docx'], data['instructions_filename']))
            
            if st.checkbox("📝 Exam (RTF)", value=True):
                exam_content = data.get('exam_rtf_bytes') or data.get('exam_rtf_content')
                if exam_content:
                    upload_files.append(('exam', exam_content, data['exam_filename']))
    
    # Upload button
    if upload_files and sharepoint_site_url:
        st.write(f"**Ready to upload {len(upload_files)} file(s) to:** `{folder_path}`")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Upload to SharePoint", use_container_width=True, type="primary"):
                upload_progress = st.progress(0)
                status_placeholder = st.empty()
                
                # Get site and drive info
                status_placeholder.write("🔍 Connecting to SharePoint...")
                site_id, site_name = get_site_id_from_url(sharepoint_site_url, access_token)
                
                if not site_id:
                    status_placeholder.error("❌ Could not access SharePoint site")
                    return
                
                drive_id = get_default_drive_id(site_id, access_token)
                if not drive_id:
                    status_placeholder.error("❌ Could not access document library")
                    return
                
                # Upload files
                success_count = 0
                results = []
                
                for i, (file_type, content, filename) in enumerate(upload_files):
                    progress = (i + 1) / len(upload_files)
                    upload_progress.progress(progress)
                    status_placeholder.write(f"📤 Uploading {filename}...")
                    
                    success, result = upload_to_sharepoint_clean(
                        content, filename, site_id, drive_id, 
                        access_token, folder_path
                    )
                    
                    if success:
                        success_count += 1
                        results.append(f"✅ **{filename}** ({format_file_size(result['size'])})")
                    else:
                        results.append(f"❌ **{filename}** - {result}")
                
                upload_progress.progress(1.0)
                status_placeholder.empty()
                
                # Show results
                if success_count > 0:
                    st.balloons()
                    st.success(f"🎉 Successfully uploaded {success_count} of {len(upload_files)} file(s)!")
                    
                    with st.expander("📋 Upload Details", expanded=False):
                        for result in results:
                            st.write(result)
                else:
                    st.error("❌ All uploads failed")
                    for result in results:
                        st.write(result)
    
    elif not upload_files:
        st.info("📋 Select files to upload above")
    
    # Sign out
    if is_authenticated:
        st.write("")
        if st.button("🔓 Sign Out"):
            # Clear all authentication session state keys
            st.session_state.sp_access_token = None
            st.session_state.access_token = None
            st.session_state.sharepoint_access_token = None
            st.session_state.sp_authenticated = False
            st.session_state.sp_user_info = None
            st.success("👋 Signed out successfully!")
            st.rerun()

# Main render function for compatibility
def render_sharepoint_ui(data):
    """Main render function for SharePoint integration"""
    render_sharepoint_upload_ui(data)
