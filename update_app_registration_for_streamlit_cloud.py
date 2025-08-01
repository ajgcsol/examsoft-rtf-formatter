#!/usr/bin/env python3
"""
Script to update Azure AD App Registration for Streamlit Cloud deployment
This fixes the Microsoft 365 authentication issues by ensuring proper configuration
"""

import requests
import json
import sys

# App Registration Details
APP_ID = "4848a7e9-327a-49ff-a789-6f8b928615b7"
TENANT_ID = "40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078"
OBJECT_ID = "20d20db1-5ad9-49aa-a372-7102f92bd94d"

def print_required_configuration():
    """Print the required configuration for the Azure AD app registration"""
    
    print("🔧 **AZURE AD APP REGISTRATION CONFIGURATION NEEDED**")
    print("=" * 60)
    print(f"App ID: {APP_ID}")
    print(f"Tenant ID: {TENANT_ID}")
    print(f"Object ID: {OBJECT_ID}")
    print()
    
    print("📋 **REQUIRED SETTINGS:**")
    print()
    
    print("1. **Authentication Settings:**")
    print("   Platform: Mobile and desktop applications")
    print("   Redirect URIs:")
    print("   - http://localhost:8501")
    print("   - https://csol-examsoft-converter.streamlit.app")
    print("   - https://login.microsoftonline.com/common/oauth2/nativeclient")
    print()
    print("   ✅ Allow public client flows: YES")
    print("   ✅ Device code flow: Enabled")
    print()
    
    print("2. **API Permissions:**")
    print("   Microsoft Graph (Application permissions):")
    print("   - Sites.ReadWrite.All")
    print("   - Files.ReadWrite.All")
    print("   - User.Read")
    print()
    print("   ⚠️  IMPORTANT: Grant admin consent for all permissions")
    print()
    
    print("3. **App Type:**")
    print("   - Public client application: YES")
    print("   - Supported account types: Accounts in this organizational directory only")
    print()
    
    print("🌐 **AZURE PORTAL STEPS:**")
    print("1. Go to https://portal.azure.com")
    print("2. Navigate to Azure Active Directory > App registrations")
    print(f"3. Find app '{APP_ID}' (ExamSoft Formatter)")
    print("4. Click on 'Authentication':")
    print("   - Add platform: Mobile and desktop applications")
    print("   - Add redirect URIs listed above")
    print("   - Enable 'Allow public client flows'")
    print("5. Click on 'API permissions':")
    print("   - Ensure all permissions listed above are present")
    print("   - Click 'Grant admin consent' if not already done")
    print("6. Save all changes")
    print()
    
    print("🚀 **VERIFICATION:**")
    print("After making these changes:")
    print("1. Wait 5-10 minutes for propagation")
    print("2. Test the Streamlit Cloud app authentication")
    print("3. Device code flow should work without infinite loops")
    print()

def generate_powershell_script():
    """Generate PowerShell script to update the app registration"""
    
    script = f'''# PowerShell script to update Azure AD App Registration for Streamlit Cloud
# Run this in Azure Cloud Shell or with Azure PowerShell module

# Connect to Azure AD (if not already connected)
# Connect-AzureAD

# App Registration details
$AppId = "{APP_ID}"
$ObjectId = "{OBJECT_ID}"

Write-Host "Updating Azure AD App Registration: $AppId" -ForegroundColor Green

# Update redirect URIs for public client
$RedirectUris = @(
    "http://localhost:8501",
    "https://csol-examsoft-converter.streamlit.app",
    "https://login.microsoftonline.com/common/oauth2/nativeclient"
)

try {{
    # Get the current app registration
    $App = Get-AzureADApplication -ObjectId $ObjectId
    
    # Update public client settings
    $App.PublicClient = $true
    $App.ReplyUrls = $RedirectUris
    
    # Apply updates
    Set-AzureADApplication -ObjectId $ObjectId -PublicClient $true -ReplyUrls $RedirectUris
    
    Write-Host "✅ Successfully updated app registration!" -ForegroundColor Green
    Write-Host "Redirect URIs updated:" -ForegroundColor Yellow
    foreach ($uri in $RedirectUris) {{
        Write-Host "  - $uri" -ForegroundColor White
    }}
    
    Write-Host ""
    Write-Host "⚠️  Please also verify API permissions and grant admin consent:" -ForegroundColor Yellow
    Write-Host "- Sites.ReadWrite.All" -ForegroundColor White
    Write-Host "- Files.ReadWrite.All" -ForegroundColor White  
    Write-Host "- User.Read" -ForegroundColor White
    
}} catch {{
    Write-Host "❌ Error updating app registration: $_.Exception.Message" -ForegroundColor Red
    Write-Host "Please update manually via Azure Portal" -ForegroundColor Yellow
}}
'''
    
    with open('update_azure_app_registration.ps1', 'w') as f:
        f.write(script)
    
    print(f"📜 PowerShell script saved as: update_azure_app_registration.ps1")
    print("Run this script in Azure Cloud Shell to update the app registration automatically")

if __name__ == "__main__":
    print_required_configuration()
    print()
    generate_powershell_script()
