"""
Script to add required Microsoft Graph permissions to the ExamSoft app registration
Run this first, then grant admin consent
"""
import subprocess
import json

def add_permissions_to_app():
    """Add Microsoft Graph permissions to the app registration"""
    
    CLIENT_ID = "4848a7e9-327a-49ff-a789-6f8b928615b7"
    
    # Microsoft Graph API Application ID (constant)
    MICROSOFT_GRAPH_API_ID = "00000003-0000-0000-c000-000000000000"
    
    # Required permissions with their Graph API IDs
    permissions = [
        {
            "id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d",  # User.Read
            "type": "Scope"  # Delegated permission
        },
        {
            "id": "205e70e5-aba6-4c52-a976-6d2d46c48043",  # Sites.Read.All
            "type": "Scope"  # Delegated permission
        },
        {
            "id": "9492366f-7969-46a4-8d15-ed1a20078fff",  # Sites.ReadWrite.All
            "type": "Scope"  # Delegated permission
        },
        {
            "id": "b633e1c5-b582-4048-a93e-9f11b44c7e96",  # Mail.Send
            "type": "Scope"  # Delegated permission
        }
    ]
    
    print("🔧 Adding Microsoft Graph Permissions to ExamSoft App")
    print("="*50)
    print(f"App ID: {CLIENT_ID}")
    print("Required Permissions:")
    for perm in permissions:
        perm_name = {
            "e1fe6dd8-ba31-4d61-89e7-88639da4683d": "User.Read",
            "205e70e5-aba6-4c52-a976-6d2d46c48043": "Sites.Read.All", 
            "9492366f-7969-46a4-8d15-ed1a20078fff": "Sites.ReadWrite.All",
            "b633e1c5-b582-4048-a93e-9f11b44c7e96": "Mail.Send"
        }.get(perm["id"], "Unknown")
        print(f"  - {perm_name} ({perm['type']})")
    print()
    
    # Build the required resource access JSON
    required_resource_access = {
        "resourceAppId": MICROSOFT_GRAPH_API_ID,
        "resourceAccess": permissions
    }
    
    # Convert to JSON string for Azure CLI
    permissions_json = json.dumps([required_resource_access])
    
    print("🔄 Adding permissions to app registration...")
    
    try:
        # Add permissions using Azure CLI
        cmd = [
            "az", "ad", "app", "update",
            "--id", CLIENT_ID,
            "--required-resource-accesses", permissions_json
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ Permissions added successfully!")
        print()
        print("🔗 Now grant admin consent using this URL:")
        print(f"https://login.microsoftonline.com/40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078/adminconsent?client_id={CLIENT_ID}&state=12345&redirect_uri=https://localhost")
        print()
        print("📋 Next steps:")
        print("1. Open the URL above in your browser")
        print("2. Sign in as Global Administrator")  
        print("3. Accept the permissions")
        print("4. Users can then sign out/in to the app")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add permissions: {e}")
        print(f"Error output: {e.stderr}")
        print()
        print("💡 Alternative: Add permissions manually in Azure Portal:")
        print("1. Go to Azure Portal > App registrations")
        print(f"2. Find app: {CLIENT_ID}")
        print("3. Go to API permissions")
        print("4. Add these Microsoft Graph delegated permissions:")
        print("   - User.Read")
        print("   - Sites.Read.All") 
        print("   - Sites.ReadWrite.All")
        print("   - Mail.Send")
        print("5. Grant admin consent")
    
    except FileNotFoundError:
        print("❌ Azure CLI not found. Please install Azure CLI first:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        print()
        print("Or add permissions manually in Azure Portal (see steps above)")

if __name__ == "__main__":
    add_permissions_to_app()