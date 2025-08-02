import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
import base64
try:
    import msal
    from examsoft_m365_config import M365_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    M365_CONFIG = {}

# Token storage file (encrypted with simple base64 for basic obfuscation)
TOKEN_CACHE_FILE = ".auth_cache.json"

def encode_token_data(data):
    """Simple encoding for token storage (not production-grade encryption)"""
    json_str = json.dumps(data)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded

def decode_token_data(encoded_data):
    """Decode token data from storage"""
    try:
        json_str = base64.b64decode(encoded_data).decode()
        return json.loads(json_str)
    except:
        return None

def save_token_to_cache(token_data):
    """Save authentication tokens to local cache file"""
    try:
        cache_data = {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'expires_in': token_data.get('expires_in', 3600),
            'expires_at': (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat(),
            'scope': token_data.get('scope', []),
            'account_info': token_data.get('account', {}),
            'saved_at': datetime.now().isoformat()
        }
        
        encoded_data = encode_token_data(cache_data)
        with open(TOKEN_CACHE_FILE, 'w') as f:
            f.write(encoded_data)
        
        return True
    except Exception as e:
        st.error(f"Failed to save authentication cache: {e}")
        return False

def load_token_from_cache():
    """Load authentication tokens from local cache file"""
    try:
        if not os.path.exists(TOKEN_CACHE_FILE):
            return None
        
        with open(TOKEN_CACHE_FILE, 'r') as f:
            encoded_data = f.read().strip()
        
        cache_data = decode_token_data(encoded_data)
        if not cache_data:
            return None
        
        # Check if token is still valid (with 5 minute buffer)
        expires_at = datetime.fromisoformat(cache_data['expires_at'])
        if datetime.now() >= expires_at - timedelta(minutes=5):
            # Token expired or about to expire
            return None
        
        return cache_data
        
    except Exception as e:
        # If any error, return None to force re-authentication
        return None

def clear_token_cache():
    """Clear the authentication cache"""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            os.remove(TOKEN_CACHE_FILE)
        return True
    except:
        return False

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token"""
    try:
        app = msal.PublicClientApplication(
            M365_CONFIG['client_id'],
            authority=M365_CONFIG['authority']
        )
        
        # Try to refresh the token
        result = app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=M365_CONFIG['scope']
        )
        
        if 'access_token' in result:
            return result
        else:
            return None
            
    except Exception as e:
        return None

def get_device_flow():
    """Start device code flow for authentication"""
    try:
        # Validate configuration silently (no st.write calls that interfere with spinner)
        if not M365_CONFIG.get('client_id'):
            raise ValueError("Client ID not found in configuration")
            
        if not M365_CONFIG.get('authority'):
            raise ValueError("Authority not found in configuration")
            
        if not M365_CONFIG.get('scope'):
            raise ValueError("Scopes not found in configuration")
        
        # Create MSAL app and device flow
        app = msal.PublicClientApplication(
            M365_CONFIG['client_id'],
            authority=M365_CONFIG['authority']
        )
        
        flow = app.initiate_device_flow(scopes=M365_CONFIG['scope'])
        
        if "user_code" not in flow:
            error_desc = flow.get('error_description', 'Unknown error')
            error_code = flow.get('error', 'unknown_error')
            raise ValueError(f"Failed to create device flow ({error_code}): {error_desc}")
        
        return app, flow
        
    except Exception as e:
        # Log error for debugging but also return the error info
        print(f"❌ Authentication error: {str(e)}")
        return None, {"error_description": str(e), "error": "device_flow_failed"}

def complete_device_flow(app, flow):
    """Complete device code flow and get access token"""
    try:
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            return result
        else:
            error_msg = result.get("error_description", "Unknown error")
            st.error(f"Authentication failed: {error_msg}")
            return None
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

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

def initialize_persistent_auth():
    """Initialize persistent authentication system with better caching"""
    
    # Initialize session state
    if 'sp_access_token' not in st.session_state:
        st.session_state.sp_access_token = None
    if 'sp_authenticated' not in st.session_state:
        st.session_state.sp_authenticated = False
    if 'sp_user_info' not in st.session_state:
        st.session_state.sp_user_info = None
    if 'auth_expires_at' not in st.session_state:
        st.session_state.auth_expires_at = None
    
    # Always try to load cached authentication first
    cached_auth = load_token_from_cache()
    if cached_auth:
        # Test if the cached token is still valid
        try:
            user_info = get_user_info(cached_auth['access_token'])
            if user_info:
                # Cached token is still valid - restore session
                st.session_state.sp_access_token = cached_auth['access_token']
                st.session_state.access_token = cached_auth['access_token']
                st.session_state.sharepoint_access_token = cached_auth['access_token']
                st.session_state.sp_authenticated = True
                st.session_state.sp_user_info = user_info
                st.session_state.auth_expires_at = cached_auth['expires_at']
                st.session_state.refresh_token = cached_auth.get('refresh_token')
                
                return True
        except:
            pass
        
        # Token invalid, try to refresh if we have a refresh token
        refresh_token = cached_auth.get('refresh_token')
        if refresh_token:
            try:
                refreshed = refresh_access_token(refresh_token)
                if refreshed and 'access_token' in refreshed:
                    # Save the new token
                    save_token_to_cache(refreshed)
                    
                    # Update session state
                    st.session_state.sp_access_token = refreshed['access_token']
                    st.session_state.access_token = refreshed['access_token']
                    st.session_state.sharepoint_access_token = refreshed['access_token']
                    st.session_state.sp_authenticated = True
                    st.session_state.sp_user_info = get_user_info(refreshed['access_token'])
                    st.session_state.auth_expires_at = (datetime.now() + timedelta(seconds=refreshed.get('expires_in', 3600))).isoformat()
                    st.session_state.refresh_token = refreshed.get('refresh_token')
                    
                    return True
            except:
                pass
        
        # Refresh failed, clear cache
        clear_token_cache()
    
    return st.session_state.sp_authenticated

def render_persistent_auth_ui():
    """Render authentication UI with persistent login - SIMPLIFIED VERSION"""
    
    # Initialize session state if needed
    if 'sp_authenticated' not in st.session_state:
        st.session_state.sp_authenticated = False
    if 'sp_access_token' not in st.session_state:
        st.session_state.sp_access_token = None
    if 'sp_user_info' not in st.session_state:
        st.session_state.sp_user_info = None
    
    # If already authenticated, show status
    if st.session_state.sp_authenticated:
        render_auth_status()
        return True
    
    # Not authenticated - show sign in UI
    st.info("🔐 **Microsoft 365 Authentication**")
    st.write("Sign in to upload files to SharePoint")
    
    # Single button authentication
    if st.button("🔑 Sign in with Microsoft 365", use_container_width=True, type="primary", key=f"auth_signin_btn_{id(st.session_state)}"):
        try:
            # Validate configuration
            if not CONFIG_AVAILABLE or not M365_CONFIG:
                st.error("❌ Configuration error - MSAL or M365 config not available")
                return False
            
            # Get device flow
            with st.spinner("Getting authentication code..."):
                app, flow = get_device_flow()
            
            if app and flow and 'user_code' in flow:
                # Show device code and auto-check
                st.success("🎯 **Authentication Code Ready!**")
                st.info(f"**Visit:** {flow['verification_uri']}")
                st.code(flow['user_code'], language=None)
                st.write("1. Click the link above")
                st.write("2. Enter the code and sign in")
                st.write("3. This page will automatically refresh when complete")
                
                # Auto-poll for completion (with reasonable timeout)
                import time
                max_attempts = 60  # 5 minutes max
                attempt = 0
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while attempt < max_attempts:
                    attempt += 1
                    progress = attempt / max_attempts
                    progress_bar.progress(progress)
                    status_text.text(f"Waiting for authentication... ({attempt}/{max_attempts})")
                    
                    try:
                        result = complete_device_flow(app, flow)
                        if result and 'access_token' in result:
                            # Success! Save and update
                            save_token_to_cache(result)
                            
                            # Set session state
                            st.session_state.sp_access_token = result['access_token']
                            st.session_state.access_token = result['access_token']
                            st.session_state.sharepoint_access_token = result['access_token']
                            st.session_state.sp_authenticated = True
                            st.session_state.sp_user_info = get_user_info(result['access_token'])
                            st.session_state.auth_expires_at = (datetime.now() + timedelta(seconds=result.get('expires_in', 3600))).isoformat()
                            
                            progress_bar.progress(1.0)
                            status_text.text("Authentication successful!")
                            st.success("🎉 Authentication successful!")
                            time.sleep(1)
                            st.rerun()
                            return True
                            
                    except Exception as e:
                        error_msg = str(e)
                        if "54005" in error_msg or "already redeemed" in error_msg:
                            # Code expired, but this is expected during polling
                            break
                        elif "authorization_pending" in error_msg or "slow_down" in error_msg:
                            # User hasn't completed auth yet, continue waiting
                            time.sleep(5)
                            continue
                        else:
                            # Other error
                            st.error(f"❌ Authentication error: {error_msg}")
                            break
                    
                    time.sleep(5)  # Wait 5 seconds between checks
                
                # Timeout or error
                progress_bar.empty()
                status_text.empty()
                st.warning("⏱️ Authentication timed out. Please try again.")
                
            else:
                st.error("❌ Failed to create authentication flow")
                
        except Exception as e:
            st.error(f"❌ Authentication error: {str(e)}")
    
    return False

def render_auth_status():
    """Render authentication status with expiration info"""
    if st.session_state.sp_authenticated and st.session_state.sp_user_info:
        user_name = st.session_state.sp_user_info.get('displayName', 'Unknown User')
        user_email = st.session_state.sp_user_info.get('mail', st.session_state.sp_user_info.get('userPrincipalName', ''))
        
        st.success(f"✅ **{user_name}**")
        st.write(f"📧 {user_email}")
        
        # Show token expiration info
        if st.session_state.auth_expires_at:
            try:
                expires_at = datetime.fromisoformat(st.session_state.auth_expires_at)
                time_left = expires_at - datetime.now()
                
                if time_left.total_seconds() > 3600:  # More than 1 hour
                    hours = int(time_left.total_seconds() // 3600)
                    st.write(f"🕒 Token expires in {hours} hours")
                elif time_left.total_seconds() > 0:  # Less than 1 hour
                    minutes = int(time_left.total_seconds() // 60)
                    st.write(f"🕒 Token expires in {minutes} minutes")
                else:
                    st.warning("🕒 Token expired - will refresh automatically")
            except:
                pass
        
        st.write("Ready for SharePoint upload")
        return True
    return False

def sign_out_persistent():
    """Sign out and clear all authentication data"""
    # Clear session state
    st.session_state.sp_access_token = None
    st.session_state.access_token = None
    st.session_state.sharepoint_access_token = None
    st.session_state.sp_authenticated = False
    st.session_state.sp_user_info = None
    st.session_state.auth_expires_at = None
    
    if 'refresh_token' in st.session_state:
        del st.session_state.refresh_token
    
    # Clear cached tokens
    clear_token_cache()
    
    return True

# Export the main functions for use in other modules
__all__ = [
    'initialize_persistent_auth',
    'render_persistent_auth_ui', 
    'render_auth_status',
    'sign_out_persistent'
]
