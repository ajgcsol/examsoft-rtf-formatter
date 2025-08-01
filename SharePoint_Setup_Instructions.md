# SharePoint Integration Setup Instructions

## Overview
The ExamSoft Formatter now supports secure Microsoft 365 authentication for uploading files directly to SharePoint. This eliminates the need for users to enter passwords and provides enterprise-grade security.

## IT Department Setup Required

### Option A: Automated Setup (Recommended) 🚀

Use the provided Azure CLI script to automatically configure everything:

#### Prerequisites:
- Azure CLI installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- Global Administrator or Application Administrator role in Azure AD

#### For Windows (PowerShell):
```powershell
# Navigate to the exam formatter directory
cd "C:\path\to\exam-formatter"

# Run the setup script
.\setup_sharepoint_integration.ps1
```

#### For Linux/Mac (Bash):
```bash
# Navigate to the exam formatter directory
cd /path/to/exam-formatter

# Make script executable
chmod +x setup_sharepoint_integration.sh

# Run the setup script
./setup_sharepoint_integration.sh
```

#### What the script does:
1. ✅ Creates Azure AD app registration
2. ✅ Configures API permissions (Sites.ReadWrite.All, Files.ReadWrite.All, User.Read)
3. ✅ Grants admin consent automatically
4. ✅ Creates client secret with 2+ year expiration
5. ✅ Generates `examsoft_m365_config.py` with all configuration values
6. ✅ Provides clear next steps

#### After running the script:
1. Copy the configuration from `examsoft_m365_config.py`
2. Update the `M365_CONFIG` in `examsoft_formatter_updated.py`
3. **Securely store the client secret** (it's only shown once!)

---

### Option B: Manual Setup (Azure Portal)

If you prefer to configure manually or don't have Azure CLI:

### Step 1: Azure App Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure the app:
   - **Name**: `ExamSoft Formatter`
   - **Supported account types**: `Accounts in this organizational directory only (Charleston School of Law only)`
   - **Redirect URI**: 
     - Type: `Web`
     - URI: `http://localhost:8501` (for local development)

### Step 2: Configure API Permissions
Add the following Microsoft Graph permissions:
- `Sites.ReadWrite.All` (Application permission)
- `Files.ReadWrite.All` (Application permission)
- `User.Read` (Delegated permission)

### Step 3: Generate Client Secret
1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Set expiration (recommend 24 months)
4. **Save the secret value** - you'll need this

### Step 4: Update Application Configuration
Edit the `M365_CONFIG` in `examsoft_formatter_updated.py`:

```python
M365_CONFIG = {
    "client_id": "YOUR-ACTUAL-CLIENT-ID-HERE",
    "client_secret": "YOUR-CLIENT-SECRET-HERE",  # Keep secure!
    "tenant_id": "charlestonlaw.edu",
    "authority": "https://login.microsoftonline.com/charlestonlaw.edu",
    "scope": ["https://graph.microsoft.com/Sites.ReadWrite.All", 
             "https://graph.microsoft.com/Files.ReadWrite.All"],
    "redirect_uri": "http://localhost:8501"
}
```

### Step 5: Admin Consent
1. In Azure Portal, go to your app registration
2. Click **API permissions**
3. Click **Grant admin consent for Charleston School of Law**

## Security Benefits

✅ **No Password Storage**: Users authenticate through Microsoft 365  
✅ **Single Sign-On**: Works with existing Charleston Law accounts  
✅ **Conditional Access**: Honors your organization's security policies  
✅ **Audit Trail**: All uploads logged in Microsoft 365 audit logs  
✅ **Token-Based**: Secure OAuth2 authentication flow  

## User Experience After Setup

1. User clicks "Sign in with Microsoft 365"
2. Browser opens to Charleston Law login page
3. User enters their normal credentials
4. User selects SharePoint site and document library
5. Files upload directly to SharePoint with proper naming convention

## File Naming Convention
Files uploaded to SharePoint will follow this format:
- Instructions: `COURSE_SECTION_PROFESSOR_ins_YYMMDD.docx`
- Exam: `COURSE_SECTION_PROFESSOR_exm_YYMMDD.rtf`

## Support Contact
For technical support with this setup, contact the application developer or your Microsoft 365 administrator.

## Testing Checklist
- [ ] App registration created
- [ ] API permissions configured and consented
- [ ] Client ID and secret updated in application
- [ ] Test authentication with a faculty member
- [ ] Verify file uploads work to SharePoint
- [ ] Confirm proper file naming and organization

## Troubleshooting

### Common Issues and Solutions

#### "Consent validation failed" Error
**Cause**: Azure AD needs time for permissions to propagate before admin consent can be granted.

**Solutions**:
1. **Wait and retry**: The updated scripts now include retry logic with delays
2. **Manual consent**: If automated consent fails, grant it manually:
   - Go to [Azure Portal](https://portal.azure.com) > Azure Active Directory > App registrations
   - Find "ExamSoft Formatter" app
   - Click **API permissions**
   - Click **Grant admin consent for Charleston School of Law**

#### "Application not found" Error
**Cause**: App registration may not have completed or was deleted.

**Solution**: Re-run the setup script or verify the app exists in Azure Portal.

#### Authentication Issues in Application
**Causes**: 
- Incorrect client ID or secret
- Tenant domain mismatch
- Missing admin consent

**Solutions**:
1. Verify `M365_CONFIG` values match the generated configuration
2. Ensure tenant domain is exactly "charlestonlaw.edu"
3. Check that admin consent was granted (green checkmarks in Azure Portal)

#### Script Permission Errors
**Cause**: Insufficient Azure AD permissions to create app registrations.

**Solution**: Ensure you have one of these roles:
- Global Administrator
- Application Administrator
- Cloud Application Administrator

### Getting Help
- **Azure AD Issues**: Contact your Microsoft 365 administrator
- **Script Issues**: Check Azure CLI is installed and you're logged in (`az account show`)
- **Application Issues**: Verify all configuration values are correct and secrets haven't expired
