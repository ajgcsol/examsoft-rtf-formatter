"""
Microsoft 365 App Registration Configuration Guide
For ExamSoft RTF Formatter with Persistent Authentication and SharePoint Upload

This guide shows what needs to be configured in Azure AD / Microsoft 365 Admin Center
for the app to work with 90-day persistent authentication and SharePoint uploads.
"""

# App Registration Settings Required
APP_REGISTRATION_CONFIG = {
    "basic_settings": {
        "name": "ExamSoft RTF Formatter",
        "supported_account_types": "Accounts in this organizational directory only (Charleston School of Law only - Single tenant)",
        "redirect_uris": [
            "http://localhost:8501",
            "http://localhost:8502", 
            "https://login.microsoftonline.com/common/oauth2/nativeclient"
        ],
        "platform_type": "Public client/native (mobile & desktop)"
    },
    
    "api_permissions": {
        "microsoft_graph": [
            {
                "permission": "Sites.ReadWrite.All",
                "type": "Delegated",
                "admin_consent": "Required",
                "description": "Read and write items and lists in all site collections"
            },
            {
                "permission": "Files.ReadWrite.All", 
                "type": "Delegated",
                "admin_consent": "Required",
                "description": "Have full access to all files user can access"
            },
            {
                "permission": "User.Read",
                "type": "Delegated", 
                "admin_consent": "Not required",
                "description": "Sign in and read user profile"
            },
            {
                "permission": "offline_access",
                "type": "Delegated",
                "admin_consent": "Not required", 
                "description": "Maintain access to data you have given it access to"
            }
        ]
    },
    
    "authentication_settings": {
        "allow_public_client_flows": True,
        "supported_account_types": "AzureADMyOrg",
        "treat_application_as_public_client": True
    },
    
    "token_configuration": {
        "access_token_lifetime": "1 hour (default)",
        "refresh_token_lifetime": "90 days (configurable)",
        "refresh_token_inactive_lifetime": "90 days",
        "single_sign_on_session_lifetime": "Until browser closed",
        "refresh_token_max_age": "90 days"
    },
    
    "conditional_access": {
        "persistent_browser_session": True,
        "sign_in_frequency": "90 days", 
        "require_compliant_device": False,
        "require_mfa": "As per organization policy"
    }
}

def print_configuration_steps():
    """Print step-by-step configuration instructions"""
    
    print("🔧 Microsoft 365 App Registration Configuration")
    print("=" * 60)
    
    print("\n📋 STEP 1: Create App Registration")
    print("-" * 40)
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory > App registrations")
    print("3. Click: + New registration")
    print("4. Name: ExamSoft RTF Formatter")
    print("5. Supported account types: Accounts in this organizational directory only")
    print("6. Redirect URI: Public client/native > http://localhost:8501")
    print("7. Click: Register")
    
    print("\n📋 STEP 2: Configure Authentication")
    print("-" * 40)
    print("1. Go to: Authentication (left menu)")
    print("2. Platform configurations:")
    print("   - Add platform: Mobile and desktop applications")
    print("   - Add redirect URIs:")
    print("     • http://localhost:8501")
    print("     • http://localhost:8502")
    print("     • https://login.microsoftonline.com/common/oauth2/nativeclient")
    print("3. Advanced settings:")
    print("   ✅ Allow public client flows: YES")
    print("   ✅ Treat application as a public client: YES")
    print("4. Click: Save")
    
    print("\n📋 STEP 3: Configure API Permissions")
    print("-" * 40)
    print("1. Go to: API permissions (left menu)")
    print("2. Click: + Add a permission")
    print("3. Microsoft Graph > Delegated permissions:")
    print("   ✅ Sites.ReadWrite.All (Admin consent required)")
    print("   ✅ Files.ReadWrite.All (Admin consent required)")
    print("   ✅ User.Read (Usually granted by default)")
    print("   ✅ offline_access (For refresh tokens)")
    print("4. Click: Add permissions")
    print("5. IMPORTANT: Click 'Grant admin consent for Charleston School of Law'")
    print("6. Wait for all permissions to show 'Granted for Charleston School of Law'")
    
    print("\n📋 STEP 4: Configure Token Lifetime Policies")
    print("-" * 40)
    print("1. Go to: Token configuration (left menu)")
    print("2. Optional claims:")
    print("   - Add optional claim for 'Access' tokens: email, preferred_username")
    print("3. For refresh token lifetime (requires PowerShell):")
    print("   Connect-AzureAD")
    print("   New-AzureADPolicy -Definition @('[{\"TokenLifetimePolicy\":{\"Version\":1,\"MaxAgeSingleFactor\":\"90.00:00:00\"}}]') -DisplayName '90DayRefreshTokenPolicy' -Type 'TokenLifetimePolicy'")
    print("   Apply to your app registration")
    
    print("\n📋 STEP 5: Get Configuration Values")
    print("-" * 40)
    print("1. Go to: Overview (left menu)")
    print("2. Copy these values for your app:")
    print("   📄 Application (client) ID: [Copy this]")
    print("   📄 Directory (tenant) ID: [Copy this]")
    print("3. Update examsoft_m365_config.py with these values")
    
    print("\n🔒 STEP 6: Conditional Access (Optional)")
    print("-" * 40)
    print("If your organization uses Conditional Access:")
    print("1. Go to: Azure AD > Security > Conditional Access")
    print("2. Create policy for persistent browser sessions")
    print("3. Set sign-in frequency to 90 days")
    print("4. Enable persistent browser session")
    
    print("\n⚠️  COMMON ISSUES & SOLUTIONS")
    print("-" * 40)
    print("Issue: 'One of the provided arguments is not acceptable'")
    print("Solutions:")
    print("✅ Ensure admin consent is granted for all permissions")
    print("✅ Verify the app is set as 'public client'")
    print("✅ Check redirect URIs match exactly")
    print("✅ Confirm tenant ID is correct")
    print("✅ Make sure Sites.ReadWrite.All permission is granted")
    
    print("\nIssue: Authentication expires too quickly")
    print("Solutions:")
    print("✅ Configure refresh token lifetime policy")
    print("✅ Ensure offline_access permission is granted")
    print("✅ Check conditional access policies")
    
    print("\nIssue: Cannot access SharePoint site")
    print("Solutions:")
    print("✅ Verify site ID is correct")
    print("✅ Check user has access to the SharePoint site")
    print("✅ Confirm Sites.ReadWrite.All permission")
    print("✅ Test with a different site ID")
    
    print(f"\n📞 NEXT STEPS")
    print("-" * 40)
    print("1. Complete the app registration configuration above")
    print("2. Update examsoft_m365_config.py with the correct client_id and tenant_id")
    print("3. Have an IT admin grant consent for the required permissions")
    print("4. Test the authentication and SharePoint upload")
    print("5. If still failing, use the site discovery script to find the correct site ID")

def generate_config_file(client_id, tenant_id):
    """Generate the configuration file content"""
    
    config_content = f'''"""
Microsoft 365 Configuration for ExamSoft RTF Formatter
Update these values with your app registration details
"""

M365_CONFIG = {{
    "client_id": "{client_id}",  # Application (client) ID from app registration
    "tenant_id": "{tenant_id}",  # Directory (tenant) ID or "charlestonlaw.edu" 
    "authority": "https://login.microsoftonline.com/{tenant_id}",
    "scope": [
        "https://graph.microsoft.com/Sites.ReadWrite.All",
        "https://graph.microsoft.com/Files.ReadWrite.All", 
        "https://graph.microsoft.com/User.Read",
        "offline_access"  # This enables refresh tokens for 90-day persistence
    ],
    "redirect_uri": "http://localhost:8501"  # Must match app registration
}}

# SharePoint Site Information
SHAREPOINT_CONFIG = {{
    "site_id": "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip",
    "site_name": "Exam Procedures",
    "folder_path": "Exam Procedures/ExamSoft/Import",
    "site_url": "https://charlestonlaw.sharepoint.com/sites/acad_affairs/Exam%20Procedures"
}}
'''
    
    return config_content

if __name__ == "__main__":
    print_configuration_steps()
    
    print("\n" + "=" * 60)
    print("Save this output and share with your IT administrator!")
    print("They will need to configure the app registration with these exact settings.")
    print("=" * 60)
