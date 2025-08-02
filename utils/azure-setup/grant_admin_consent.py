"""
Script to grant admin consent for Microsoft Graph API permissions
Run this as a Global Administrator
"""
import requests
import json

def grant_admin_consent():
    """
    Grant admin consent for the ExamSoft RTF Formatter app
    You'll need to fill in your tenant ID and app ID
    """
    
    # Charleston School of Law App Registration Details:
    TENANT_ID = "40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078"  # Charleston Law tenant ID
    CLIENT_ID = "4848a7e9-327a-49ff-a789-6f8b928615b7"  # ExamSoft Formatter app ID
    
    # Required permissions for the app
    permissions_to_grant = [
        "User.Read",           # Read user profile
        "Sites.Read.All",      # Read SharePoint sites
        "Sites.ReadWrite.All", # Write to SharePoint sites  
        "Mail.Send"            # Send emails
    ]
    
    print("🔧 Admin Consent Grant Script")
    print("="*40)
    print(f"Tenant ID: {TENANT_ID}")
    print(f"App ID: {CLIENT_ID}")
    print(f"Permissions: {', '.join(permissions_to_grant)}")
    print()
    
    if TENANT_ID == "YOUR_TENANT_ID_HERE" or CLIENT_ID == "YOUR_APP_CLIENT_ID_HERE":
        print("❌ Please fill in TENANT_ID and CLIENT_ID first!")
        return
    
    # Build admin consent URL
    consent_url = (
        f"https://login.microsoftonline.com/{TENANT_ID}/adminconsent?"
        f"client_id={CLIENT_ID}&"
        f"state=12345&"
        f"redirect_uri=https://localhost"
    )
    
    print("🔗 Admin Consent URL:")
    print(consent_url)
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Sign in as Global Administrator")
    print("4. Review and accept the permissions")
    print("5. You'll be redirected to localhost (this is normal)")
    print("6. Users can now sign out/in to get new permissions")
    print()
    
    return consent_url

def get_tenant_and_app_info():
    """
    Helper to find your tenant and app information
    """
    print("🔍 To find your Tenant ID and App ID:")
    print()
    print("TENANT ID:")
    print("- Go to: https://portal.azure.com")
    print("- Azure Active Directory > Overview")
    print("- Copy 'Tenant ID'")
    print()
    print("APP ID (Client ID):")
    print("- Go to: Azure Active Directory > App registrations")
    print("- Find 'ExamSoft RTF Formatter' (or your app name)")
    print("- Copy 'Application (client) ID'")
    print()

if __name__ == "__main__":
    print("Microsoft Graph Admin Consent Script")
    print("====================================")
    
    choice = input("1. Grant admin consent\n2. Get tenant/app info\nChoice (1/2): ")
    
    if choice == "1":
        grant_admin_consent()
    elif choice == "2":
        get_tenant_and_app_info()
    else:
        print("Invalid choice")