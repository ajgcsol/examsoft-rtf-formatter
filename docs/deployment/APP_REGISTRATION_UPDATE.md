# App Registration Update for Email Functionality

## Required Microsoft Graph API Permissions

To enable email functionality, you need to add these permissions to your Azure App Registration:

### 1. Mail.Send Permission
- **Type**: Delegated permission
- **Permission**: `Mail.Send`
- **Description**: Allows the app to send emails as the signed-in user

### 2. User.Read Permission (if not already added)
- **Type**: Delegated permission  
- **Permission**: `User.Read`
- **Description**: Allows reading basic user profile

## How to Update App Registration:

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to**: Azure Active Directory > App registrations
3. **Find your app**: "ExamSoft RTF Formatter" (or your app name)
4. **Click on**: API permissions
5. **Add permission** > Microsoft Graph > Delegated permissions
6. **Search and select**: `Mail.Send`
7. **Click**: Add permissions
8. **Admin consent**: Click "Grant admin consent for [Your Organization]"

## IT SharePoint Site Setup

For the IT SharePoint site option, you need to:

1. **Get the IT Site ID**:
   - Go to your IT SharePoint site
   - Use this PowerShell command or Graph API call:
   ```
   GET https://graph.microsoft.com/v1.0/sites/[your-tenant].sharepoint.com:/sites/[it-site-name]
   ```
   
2. **Update the site configuration** in `streamlit_app_fixed.py`:
   ```python
   "IT Department": {
       "site_id": "YOUR_ACTUAL_IT_SITE_ID_HERE", 
       "path": "ExamSoft/Import/",
       "description": "IT managed site with faculty access"
   }
   ```

3. **Set up folder permissions**:
   - Create `/ExamSoft/Import/` folder structure
   - Grant faculty read/write access to this folder only
   - Do not inherit permissions from parent site

## Testing the Email Functionality

Once permissions are granted:

1. Sign out and sign back in to the app
2. Process an exam 
3. Check the "Send email notification" option
4. Add recipient email addresses
5. Customize the subject and message
6. Upload and send

The app will send emails with:
- File links to uploaded SharePoint documents
- Summary of processed questions
- Custom message from the user

## Security Notes

- Email permissions are delegated (user context)
- Emails are sent from the authenticated user's account
- SharePoint uploads respect site-level permissions
- No additional authentication required for email after initial consent