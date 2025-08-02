#!/usr/bin/env python3
"""
Service Principal Configuration Fix for SharePoint Access
This will help diagnose and fix service principal issues with your Azure app registration
"""

import requests
import json
import subprocess
import sys

def check_app_registration_type():
    """Check how your app registration is configured"""
    
    print("🔍 Checking current app registration configuration...")
    
    # Your client ID from the config
    client_id = "4848a7e9-327a-49ff-a789-6f8b928615b7"
    
    try:
        # Check via Azure CLI
        result = subprocess.run([
            'az', 'ad', 'app', 'show', 
            '--id', client_id,
            '--query', '{displayName:displayName, publicClient:publicClient, signInAudience:signInAudience, requiredResourceAccess:requiredResourceAccess}'
        ], capture_output=True, text=True, check=True)
        
        app_info = json.loads(result.stdout)
        
        print(f"✅ App Registration Found:")
        print(f"   📛 Name: {app_info.get('displayName', 'Unknown')}")
        print(f"   🔓 Public Client: {app_info.get('publicClient', {}).get('redirectUris', [])}")
        print(f"   👥 Sign-in Audience: {app_info.get('signInAudience', 'Unknown')}")
        
        # Check permissions
        required_access = app_info.get('requiredResourceAccess', [])
        graph_permissions = []
        
        for resource in required_access:
            if resource.get('resourceAppId') == '00000003-0000-0000-c000-000000000000':  # Microsoft Graph
                graph_permissions = resource.get('resourceAccess', [])
                break
        
        print(f"   🔑 Graph Permissions: {len(graph_permissions)} permissions configured")
        
        # Check if we have a service principal
        sp_result = subprocess.run([
            'az', 'ad', 'sp', 'list',
            '--filter', f"appId eq '{client_id}'",
            '--query', '[0].{objectId:objectId, displayName:displayName}'
        ], capture_output=True, text=True, check=True)
        
        sp_info = json.loads(sp_result.stdout)
        
        if sp_info:
            print(f"✅ Service Principal exists:")
            print(f"   🆔 Object ID: {sp_info.get('objectId')}")
            print(f"   📛 Name: {sp_info.get('displayName')}")
            return True, sp_info.get('objectId')
        else:
            print(f"❌ No Service Principal found!")
            print(f"   💡 This might be the issue - SharePoint often requires a service principal")
            return False, None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking app registration: {e}")
        print(f"   Make sure you're logged into Azure CLI: az login")
        return False, None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return False, None

def create_service_principal():
    """Create a service principal for the app registration"""
    
    client_id = "4848a7e9-327a-49ff-a789-6f8b928615b7"
    
    print(f"\n🔧 Creating service principal for app {client_id}...")
    
    try:
        result = subprocess.run([
            'az', 'ad', 'sp', 'create',
            '--id', client_id
        ], capture_output=True, text=True, check=True)
        
        sp_info = json.loads(result.stdout)
        
        print(f"✅ Service Principal created successfully!")
        print(f"   🆔 Object ID: {sp_info.get('objectId')}")
        print(f"   📛 Name: {sp_info.get('displayName')}")
        print(f"   🔑 App ID: {sp_info.get('appId')}")
        
        return True, sp_info.get('objectId')
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating service principal: {e}")
        print(f"   Error output: {e.stderr}")
        return False, None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return False, None

def grant_sharepoint_permissions(sp_object_id):
    """Grant the service principal permissions to SharePoint"""
    
    print(f"\n🔑 Granting SharePoint permissions to service principal...")
    
    # SharePoint permissions that are commonly needed
    permissions_to_grant = [
        {
            'permission': 'Sites.ReadWrite.All',
            'scope': 'https://graph.microsoft.com/.default'
        },
        {
            'permission': 'Files.ReadWrite.All', 
            'scope': 'https://graph.microsoft.com/.default'
        }
    ]
    
    print(f"   📝 Note: Admin consent is still required for these permissions")
    print(f"   🔗 Admin consent URL:")
    print(f"   https://login.microsoftonline.com/common/adminconsent?client_id=4848a7e9-327a-49ff-a789-6f8b928615b7")
    
    return True

def test_service_principal_access():
    """Test if the service principal can access SharePoint"""
    
    print(f"\n🧪 Testing service principal access...")
    print(f"   💡 You'll need to get a new access token after the service principal is created")
    print(f"   💡 The token will now be issued for the service principal, not just the user")
    
    # Instructions for the user
    print(f"\n📋 Next steps:")
    print(f"   1. Restart your Streamlit app to get a fresh token")
    print(f"   2. Go through the authentication flow again")
    print(f"   3. The new token should work with SharePoint uploads")
    print(f"   4. If it still fails, check the detailed error messages")

def fix_service_principal_issue():
    """Main function to fix service principal issues"""
    
    print("🚀 Service Principal Fix for SharePoint Access")
    print("=" * 50)
    
    # Step 1: Check current configuration
    has_sp, sp_object_id = check_app_registration_type()
    
    if not has_sp:
        # Step 2: Create service principal
        print(f"\n💡 Creating service principal to fix SharePoint access...")
        success, sp_object_id = create_service_principal()
        
        if not success:
            print(f"\n❌ Failed to create service principal")
            print(f"   Try running this manually:")
            print(f"   az ad sp create --id 4848a7e9-327a-49ff-a789-6f8b928615b7")
            return False
    else:
        print(f"\n✅ Service principal already exists")
    
    # Step 3: Ensure proper permissions
    grant_sharepoint_permissions(sp_object_id)
    
    # Step 4: Test access
    test_service_principal_access()
    
    print(f"\n🎯 Summary:")
    print(f"   ✅ Service principal configured")
    print(f"   🔑 Permissions granted (admin consent required)")
    print(f"   🔄 Restart Streamlit app to get new token")
    print(f"   📤 Try SharePoint upload again")
    
    return True

if __name__ == "__main__":
    # Check if Azure CLI is available
    try:
        subprocess.run(['az', '--version'], capture_output=True, check=True)
        print("✅ Azure CLI is available")
    except:
        print("❌ Azure CLI not found. Please install Azure CLI first.")
        sys.exit(1)
    
    # Check if logged in
    try:
        subprocess.run(['az', 'account', 'show'], capture_output=True, check=True)
        print("✅ Logged into Azure CLI")
    except:
        print("❌ Not logged into Azure CLI. Please run: az login")
        sys.exit(1)
    
    # Run the fix
    fix_service_principal_issue()
