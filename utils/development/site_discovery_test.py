#!/usr/bin/env python3
"""
Site Discovery Test
Try to discover the correct site ID and validate access
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
    st.set_page_config(page_title="Site Discovery Test", layout="wide")
    
    st.title("🔍 SharePoint Site Discovery Test")
    st.info("Let's discover the correct site ID and test different access methods")
    
    # Get authentication
    with st.sidebar:
        st.header("🔑 Authentication")
        initialize_persistent_auth()
        is_authenticated = render_persistent_auth_ui()
    
    if is_authenticated:
        access_token = st.session_state.sp_access_token
        st.success("✅ Authenticated!")
        
        # Site discovery tests
        st.header("🔍 Site Discovery Methods")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Method 1: Search by URL", type="primary"):
                discover_site_by_url(access_token)
        
        with col2:
            if st.button("Method 2: List All Sites"):
                list_all_sites(access_token)
        
        st.header("📋 Direct Site Tests")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("Test Current Site ID"):
                test_current_site_id(access_token)
        
        with col4:
            if st.button("Test Root Site"):
                test_root_site(access_token)
        
    else:
        st.warning("⚠️ Please authenticate first")

def discover_site_by_url(access_token):
    """Try to discover site by URL"""
    
    with st.expander("🔍 Site Discovery by URL", expanded=True):
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        
        # Try to discover the site using the known URL
        site_urls = [
            "charlestonlaw.sharepoint.com,/sites/acad_affairs",
            "charlestonlaw.sharepoint.com:/sites/acad_affairs",
            "charlestonlaw.sharepoint.com:/sites/acad_affairs:",
        ]
        
        for site_url in site_urls:
            try:
                encoded_url = quote(site_url, safe=':,/')
                discovery_url = f"https://graph.microsoft.com/v1.0/sites/{encoded_url}"
                
                st.write(f"🔍 Trying: `{discovery_url}`")
                
                response = requests.get(discovery_url, headers=headers)
                
                if response.status_code == 200:
                    site_data = response.json()
                    st.success(f"✅ Found site: {site_data.get('displayName')}")
                    st.write(f"**Site ID:** `{site_data.get('id')}`")
                    st.write(f"**Web URL:** {site_data.get('webUrl')}")
                    st.json(site_data)
                    return site_data.get('id')
                else:
                    st.error(f"❌ Failed: {response.status_code}")
                    if response.status_code != 404:
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
            except Exception as e:
                st.error(f"❌ Exception: {str(e)}")
        
        st.warning("No site found with URL discovery method")
        return None

def list_all_sites(access_token):
    """List all available sites"""
    
    with st.expander("📋 All Available Sites", expanded=True):
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        
        try:
            # List all sites
            sites_url = "https://graph.microsoft.com/v1.0/sites"
            response = requests.get(sites_url, headers=headers)
            
            if response.status_code == 200:
                sites_data = response.json()
                sites = sites_data.get('value', [])
                
                st.success(f"✅ Found {len(sites)} sites")
                
                for site in sites:
                    with st.container():
                        st.write(f"**{site.get('displayName')}**")
                        st.write(f"ID: `{site.get('id')}`")
                        st.write(f"URL: {site.get('webUrl')}")
                        
                        # Check if this looks like our target site
                        if 'acad' in site.get('webUrl', '').lower() or 'affairs' in site.get('displayName', '').lower():
                            st.info("🎯 This might be our target site!")
                            
                        st.divider()
            else:
                st.error(f"❌ Failed to list sites: {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.text(response.text)
                    
        except Exception as e:
            st.error(f"❌ Exception: {str(e)}")

def test_current_site_id(access_token):
    """Test the current hardcoded site ID"""
    
    with st.expander("🧪 Testing Current Site ID", expanded=True):
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        
        current_site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
        
        st.write(f"Current Site ID: `{current_site_id}`")
        
        # Test different endpoints
        endpoints = [
            f"https://graph.microsoft.com/v1.0/sites/{current_site_id}",
            f"https://graph.microsoft.com/beta/sites/{current_site_id}",
        ]
        
        for endpoint in endpoints:
            try:
                st.write(f"🔍 Testing: `{endpoint}`")
                response = requests.get(endpoint, headers=headers)
                
                st.write(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    site_data = response.json()
                    st.success(f"✅ Success: {site_data.get('displayName')}")
                    st.json(site_data)
                else:
                    st.error(f"❌ Failed")
                    try:
                        error_data = response.json()
                        st.json(error_data)
                    except:
                        st.text(response.text)
                        
            except Exception as e:
                st.error(f"❌ Exception: {str(e)}")

def test_root_site(access_token):
    """Test accessing the root site"""
    
    with st.expander("🏠 Testing Root Site Access", expanded=True):
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        
        try:
            # Test root site
            root_url = "https://graph.microsoft.com/v1.0/sites/root"
            response = requests.get(root_url, headers=headers)
            
            st.write(f"🔍 Testing: `{root_url}`")
            st.write(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                site_data = response.json()
                st.success(f"✅ Root site: {site_data.get('displayName')}")
                st.json(site_data)
            else:
                st.error(f"❌ Failed")
                try:
                    error_data = response.json()
                    st.json(error_data)
                except:
                    st.text(response.text)
                    
        except Exception as e:
            st.error(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    main()
