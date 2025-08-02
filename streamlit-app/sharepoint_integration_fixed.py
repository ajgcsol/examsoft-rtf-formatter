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
            return result["access_token"]
        else:
            error_msg = result.get("error_description", "Unknown error")
            st.error(f"Authentication failed: {error_msg}")
            return None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

def get_site_id_from_url(site_url, access_token):
    """Extract site ID from SharePoint site URL"""
    try:
        from urllib.parse import urlparse
        
        parsed_url = urlparse(site_url)
        hostname = parsed_url.hostname
        site_path = parsed_url.path
        
        st.write(f"🔍 **Site ID Debug:**")
        st.write(f"- Input Site URL: {site_url}")
        st.write(f"- Expected Site URL: https://charlestonlaw.sharepoint.com/sites/acad_affairs")
        st.write(f"- Parsed Hostname: {hostname}")
        st.write(f"- Parsed Site Path: {site_path}")
        
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
        
        st.write(f"- Site API URL: {site_api_url}")
        
        response = requests.get(site_api_url, headers=headers)
        
        st.write(f"- Site Response Status: {response.status_code}")
        
        if response.status_code == 200:
            site_data = response.json()
            st.write(f"- Site ID: {site_data['id']}")
            st.write(f"- Site Name: {site_data.get('displayName', 'Unknown')}")
            st.write(f"- Site Web URL: {site_data.get('webUrl', 'Unknown')}")
            return site_data['id'], site_data.get('displayName', 'Unknown')
        else:
            st.error(f"Could not access site: {response.status_code} - {response.text}")
            st.write(f"**Site Error Details:** {response.text}")
            return None, None
            
    except Exception as e:
        st.error(f"Error getting site ID: {str(e)}")
        return None, None

def get_default_drive_id(site_id, access_token):
    """Get the default drive ID for the site (usually Documents library)"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Get the default drive (usually 'Documents' library)
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
        st.write(f"🔍 **Drive Selection Debug:**")
        st.write(f"- Drive API URL: `{drive_url}`")
        
        response = requests.get(drive_url, headers=headers)
        
        st.write(f"- Drive Response Status: **{response.status_code}**")
        
        if response.status_code == 200:
            drive_data = response.json()
            st.write(f"- 📁 **Drive ID**: `{drive_data['id']}`")
            st.write(f"- 📁 **Drive Name**: **{drive_data.get('name', 'Unknown')}**")
            st.write(f"- 🌐 **Drive Web URL**: {drive_data.get('webUrl', 'Unknown')}")
            
            # Also list all drives to see if there's an "Exam Procedures" drive
            st.write("**📂 Checking for other drives on this site:**")
            list_drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
            drives_response = requests.get(list_drives_url, headers=headers)
            
            if drives_response.status_code == 200:
                drives_data = drives_response.json()
                all_drives = drives_data.get('value', [])
                st.write(f"- Found **{len(all_drives)}** drive(s) on this site:")
                for i, drive in enumerate(all_drives, 1):
                    drive_name = drive.get('name', 'Unknown')
                    drive_web_url = drive.get('webUrl', 'No URL')
                    st.write(f"  {i}. **{drive_name}** - `{drive['id']}`")
                    st.write(f"     URL: {drive_web_url}")
                
                # Check if there's an "Exam Procedures" drive or folder
                exam_drive = None
                for drive in all_drives:
                    if 'exam' in drive.get('name', '').lower() or 'procedures' in drive.get('name', '').lower():
                        exam_drive = drive
                        break
                
                if exam_drive:
                    st.success(f"🎯 **Found Exam-related drive**: {exam_drive['name']}")
                    return exam_drive['id']
                else:
                    st.info(f"ℹ️ **Using default Documents drive**: {drive_data.get('name', 'Documents')}")
            
            return drive_data['id']
        else:
            st.error(f"Could not access site drive: {response.status_code} - {response.text}")
            with st.expander("🔍 Drive Error Details"):
                st.code(response.text)
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
            
            # **FIX FOR PATH DUPLICATION**: Smart detection for Teams-enabled SharePoint sites
            # If we detect "Exam Procedures" appears twice in sequence, skip the first one
            if len(path_parts) >= 3 and path_parts[1] == "Exam Procedures" and path_parts[2] == "Exam Procedures":
                st.write("🔧 **Query Path Duplication Detected**: Skipping first 'Exam Procedures' to prevent query issue")
                # Skip the first "Exam Procedures" part to prevent duplication
                path_parts = [''] + path_parts[2:]  # Keep empty first element, skip duplicate
                st.write(f"- 🛠️ **Corrected Query Path Parts**: `{path_parts}`")
            
            encoded_parts = [quote(part) if part else '' for part in path_parts]
            encoded_folder_path = '/'.join(encoded_parts)
            
            query_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{encoded_folder_path}:/children"
        else:
            query_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root/children"
        
        st.write(f"🔍 **Folder Query Debug:**")
        st.write(f"- 📁 **Input Folder Path**: `{folder_path if folder_path else '(root)'}`")
        st.write(f"- 🧹 **Cleaned Path**: `{folder_path if folder_path else '(root)'}`")
        st.write(f"- 🔗 **Encoded Path**: `{encoded_folder_path if folder_path else '(root)'}`")
        st.write(f"- 🎯 **Expected**: `/Exam%20Procedures/ExamSoft/Import`")
        st.write(f"- 🌐 **Query URL**: `{query_url}`")
        
        st.write("**📡 Making API request...**")
        
        response = requests.get(query_url, headers=headers)
        st.write(f"- 📊 **Response Status**: **{response.status_code}** {'✅' if response.status_code == 200 else '❌'}")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('value', [])
            st.write(f"- 📁 **Found**: **{len(files)}** item(s) in folder")
            
            if files:
                st.success("� **Folder Contents Found:**")
                for i, item in enumerate(files, 1):
                    name = item.get('name', 'Unknown')
                    size = item.get('size', 0)
                    created = item.get('createdDateTime', 'Unknown')
                    modified = item.get('lastModifiedDateTime', 'Unknown')
                    web_url = item.get('webUrl', 'No URL')
                    
                    # Format file size
                    if size > 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    elif size > 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size} bytes"
                    
                    st.write(f"**{i}. 📄 {name}** ({size_str})")
                    st.write(f"   📅 Created: {created[:10] if len(created) > 10 else created}")
                    st.write(f"   📝 Modified: {modified[:10] if len(modified) > 10 else modified}")
                    st.write(f"   🔗 URL: [Open in SharePoint]({web_url})")
                    st.write("---")
            else:
                st.info("📭 **Folder is empty** - No files found")
            
            return True, files
        else:
            st.error(f"❌ **Query Failed**: Status {response.status_code}")
            with st.expander("🔍 Error Details"):
                st.code(response.text)
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
            
            # **FIX FOR PATH DUPLICATION**: Smart detection for Teams-enabled SharePoint sites
            # If we detect "Exam Procedures" appears twice in sequence, skip the first one
            if len(path_parts) >= 3 and path_parts[1] == "Exam Procedures" and path_parts[2] == "Exam Procedures":
                st.write("🔧 **Path Duplication Detected**: Skipping first 'Exam Procedures' to prevent /Exam Procedures/Exam Procedures/ issue")
                # Skip the first "Exam Procedures" part to prevent duplication
                path_parts = [''] + path_parts[2:]  # Keep empty first element, skip duplicate
                st.write(f"- 🛠️ **Corrected Path Parts**: `{path_parts}`")
            
            encoded_parts = [quote(part) if part else '' for part in path_parts]
            encoded_folder_path = '/'.join(encoded_parts)
            
            upload_path = f"{encoded_folder_path}/{quote(filename)}"
        else:
            upload_path = f"/{quote(filename)}"
        
        # Microsoft Graph API endpoint for file upload with folder path
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{upload_path}:/content"
        
        # Debug information
        st.write(f"📤 **Upload Debug:**")
        st.write(f"- 📄 **Filename**: `{filename}`")
        st.write(f"- 📁 **Input Folder Path**: `{folder_path if folder_path else '(root)'}`")
        st.write(f"- 🧹 **Cleaned Path**: `{folder_path if folder_path else '(root)'}`")
        st.write(f"- 🔧 **Path Parts**: `{path_parts}`")
        st.write(f"- 🔗 **Encoded Parts**: `{encoded_parts}`")
        st.write(f"- 🎯 **Final Encoded Path**: `{encoded_folder_path if folder_path else '(root)'}`")
        st.write(f"- 📍 **Complete Upload Path**: `{upload_path}`")
        st.write(f"- 🌐 **Upload URL**: `{upload_url}`")
        st.write(f"- 📊 **File Size**: {len(file_content) if isinstance(file_content, (str, bytes)) else 'Unknown'} bytes")
        st.write(f"- ✅ **Expected Result**: File should appear in Documents/Exam Procedures/ExamSoft/Import")
        
        st.write("**📡 Uploading file...**")
        
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
        elif hasattr(file_content, 'read'):
            file_content = file_content.read()
        
        response = requests.put(upload_url, headers=headers, data=file_content)
        
        st.write(f"- 📊 **Upload Response Status**: **{response.status_code}** {'✅' if response.status_code in [200, 201] else '❌'}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            file_size = response_data.get('size', len(file_content) if isinstance(file_content, bytes) else 0)
            
            st.success("🎉 **Upload Successful!**")
            
            # Path verification for debugging duplication fix
            st.write(f"🔍 **Path Verification**:")
            st.write(f"- 🎯 **Target Path**: `Exam Procedures/ExamSoft/Import`")
            st.write(f"- 🌐 **Actual File URL**: {file_url}")
            if '/Exam%20Procedures/Exam%20Procedures/' in file_url:
                st.error("❌ **PATH DUPLICATION DETECTED IN RESPONSE URL** - Fix may need adjustment")
            elif '/Exam%20Procedures/ExamSoft/' in file_url:
                st.success("✅ **Correct path confirmed** - No duplication detected")
            else:
                st.warning("⚠️ **Unexpected path structure** - Please verify location manually")
            
            # Create expandable success details
            with st.expander("📋 View Upload Details", expanded=False):
                st.write(f"**📁 SharePoint Location**: [{format_path_readable(upload_path)}]({file_url})")
                st.write(f"**🌐 File URL**: {file_url}")
                st.write(f"**📏 File Size**: {format_file_size(file_size)}")
                st.write(f"**📅 Created**: {response_data.get('createdDateTime', 'N/A')}")
                st.write(f"**👤 Created By**: {response_data.get('createdBy', {}).get('user', {}).get('displayName', 'N/A')}")
                st.write(f"**🆔 File ID**: {response_data.get('id', 'N/A')}")
            
            return True, f"✅ Successfully uploaded **{filename}** to SharePoint!\n🔗 Direct link: {file_url}"
        else:
            st.error("❌ **Upload Failed!**")
            
            # Create expandable error details
            with st.expander("🚨 View Error Details", expanded=True):
                st.write(f"**📊 Response Status**: `{response.status_code}` ❌")
                
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_info = error_data['error']
                        st.write(f"**🏷️ Error Code**: `{error_info.get('code', 'Unknown')}`")
                        st.write(f"**📝 Error Message**: {error_info.get('message', 'No message')}")
                        
                        if 'innerError' in error_info:
                            st.write(f"**🔍 Inner Error**: {error_info['innerError']}")
                    else:
                        st.write(f"**📄 Response Body**: {error_data}")
                        
                except:
                    st.write(f"**📄 Raw Response**: {response.text}")
                
                st.write(f"**🔗 Request URL**: {upload_url}")
                st.write(f"**📍 Upload Path**: {upload_path}")
            
            return False, f"❌ Upload failed: {response.status_code} - {response.text}"
            
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
            
            # Authentication flow
            if st.session_state.access_token is None:
                st.write("**Step 1: Authentication**")
                
                if st.session_state.auth_step == 'initial':
                    if st.button("🔑 Sign in with Microsoft 365"):
                        with st.spinner("Starting authentication..."):
                            app, flow = get_device_flow()
                            if app and flow:
                                st.session_state.auth_app = app
                                st.session_state.auth_flow = flow
                                st.session_state.auth_step = 'device_code'
                                # Don't use st.rerun() - let natural page refresh handle state change
                
                elif st.session_state.auth_step == 'device_code':
                    if hasattr(st.session_state, 'auth_flow'):
                        st.info(f"**Please visit:** {st.session_state.auth_flow['verification_uri']}")
                        st.code(st.session_state.auth_flow['user_code'])
                        st.write("After entering the code, click the button below:")
                        
                        if st.button("✅ I've entered the code - Complete sign in"):
                            with st.spinner("Completing authentication..."):
                                token = complete_device_flow(st.session_state.auth_app, st.session_state.auth_flow)
                                if token:
                                    st.session_state.access_token = token
                                    st.session_state.sharepoint_access_token = token  # Also store with this key
                                    st.session_state.auth_step = 'complete'
                                    st.success("🎉 Authentication successful!")
                                    # Don't use st.rerun() - let natural page refresh handle state change
                                else:
                                    st.session_state.auth_step = 'initial'
                                    # Don't use st.rerun() - let natural page refresh handle state change
            else:
                st.success("✅ Authenticated with Microsoft 365")
                
                st.write("**Step 2: SharePoint Site Configuration**")
                
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
                
                # Buttons
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
                                    status_placeholder.write("🔍 Querying folder contents...")
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
                        if st.button("🚀 Upload to SharePoint", use_container_width=True):
                            upload_progress = st.progress(0)
                            status_placeholder = st.empty()
                            
                            # Get site ID and drive ID
                            status_placeholder.write("🔍 Getting SharePoint site information...")
                            site_id, site_name = get_site_id_from_url(sharepoint_site_url, st.session_state.access_token)
                            
                            if not site_id:
                                status_placeholder.error("❌ Could not access SharePoint site. Please check the URL and permissions.")
                            else:
                                drive_id = get_default_drive_id(site_id, st.session_state.access_token)
                                if not drive_id:
                                    status_placeholder.error("❌ Could not access SharePoint document library.")
                                else:
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
                    st.session_state.sharepoint_access_token = None
                    st.session_state.auth_step = 'initial'
                    st.success("👋 Successfully signed out!")
                    # Don't use st.rerun() - let natural page refresh handle state change
                    
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
