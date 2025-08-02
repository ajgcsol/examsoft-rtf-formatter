# Azure Portal: Add Permissions to ExamSoft App Registration

## Step 1: Find Your App Registration

1. Go to: https://portal.azure.com
2. Sign in as Global Administrator
3. Search for "App registrations" in the top search bar
4. Click on "App registrations"
5. Search for: `4848a7e9-327a-49ff-a789-6f8b928615b7`
6. Click on the "ExamSoft Formatter" app

## Step 2: Add API Permissions

1. In the left sidebar, click **"API permissions"**
2. You should see current permissions (probably just User.Read)
3. Click **"+ Add a permission"**
4. Click **"Microsoft Graph"**
5. Click **"Delegated permissions"**

## Step 3: Add Each Required Permission

**Add Sites.Read.All:**
1. In the search box, type: `Sites.Read.All`
2. Check the box next to `Sites.Read.All`
3. Click **"Add permissions"**

**Add Sites.ReadWrite.All:**
1. Click **"+ Add a permission"** again
2. Click **"Microsoft Graph"** > **"Delegated permissions"**
3. In the search box, type: `Sites.ReadWrite.All`
4. Check the box next to `Sites.ReadWrite.All`
5. Click **"Add permissions"**

**Add Mail.Send:**
1. Click **"+ Add a permission"** again
2. Click **"Microsoft Graph"** > **"Delegated permissions"**
3. In the search box, type: `Mail.Send`
4. Check the box next to `Mail.Send`
5. Click **"Add permissions"**

## Step 4: Grant Admin Consent

1. After adding all permissions, you should see 4 permissions listed:
   - User.Read ✅
   - Sites.Read.All ⚠️ (needs admin consent)
   - Sites.ReadWrite.All ⚠️ (needs admin consent)
   - Mail.Send ⚠️ (needs admin consent)

2. Click **"Grant admin consent for Charleston School of Law"**
3. Click **"Yes"** when prompted
4. All permissions should now show green checkmarks ✅

## Step 5: Verify Success

After granting consent, you should see:
- ✅ User.Read (Granted for Charleston School of Law)
- ✅ Sites.Read.All (Granted for Charleston School of Law)
- ✅ Sites.ReadWrite.All (Granted for Charleston School of Law)
- ✅ Mail.Send (Granted for Charleston School of Law)

## Step 6: Test the App

1. Go back to your ExamSoft app
2. Sign out if currently signed in
3. Sign back in
4. The SharePoint site dropdown and email features should now work!

---

## Alternative: PowerShell Script (if you prefer)

If you have PowerShell with Azure AD module:

```powershell
# Connect to Azure AD
Connect-AzureAD

# Get the app
$app = Get-AzureADApplication -Filter "AppId eq '4848a7e9-327a-49ff-a789-6f8b928615b7'"

# Microsoft Graph Service Principal
$graphSP = Get-AzureADServicePrincipal -Filter "AppId eq '00000003-0000-0000-c000-000000000000'"

# Required permissions
$permissions = @(
    @{ Id = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"; Type = "Scope" }  # User.Read
    @{ Id = "205e70e5-aba6-4c52-a976-6d2d46c48043"; Type = "Scope" }  # Sites.Read.All
    @{ Id = "9492366f-7969-46a4-8d15-ed1a20078fff"; Type = "Scope" }  # Sites.ReadWrite.All
    @{ Id = "b633e1c5-b582-4048-a93e-9f11b44c7e96"; Type = "Scope" }  # Mail.Send
)

# Add permissions
$requiredAccess = @{
    ResourceAppId = "00000003-0000-0000-c000-000000000000"
    ResourceAccess = $permissions
}

Set-AzureADApplication -ObjectId $app.ObjectId -RequiredResourceAccess $requiredAccess
```

The manual Azure Portal method is probably easier and more reliable.