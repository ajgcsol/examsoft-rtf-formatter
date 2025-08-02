# Azure CLI PowerShell Script to set up SharePoint integration for ExamSoft Formatter
# Run this script as an Azure AD administrator

param(
    [string]$TenantDomain = "charlestonlaw.edu",
    [string]$AppName = "ExamSoft Formatter",
    [string]$RedirectUri = "http://localhost:8501"
)

# Enable strict error handling
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up ExamSoft Formatter SharePoint Integration..." -ForegroundColor Green
Write-Host ""

Write-Host "📋 Configuration:" -ForegroundColor Blue
Write-Host "  App Name: $AppName"
Write-Host "  Redirect URI: $RedirectUri" 
Write-Host "  Tenant: $TenantDomain"
Write-Host ""

# Check if user is logged in to Azure CLI
Write-Host "🔍 Checking Azure CLI login status..." -ForegroundColor Blue
try {
    $null = az account show 2>$null
    Write-Host "✅ Azure CLI authenticated" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure CLI" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}

# Get tenant ID
Write-Host "🔍 Getting tenant information..." -ForegroundColor Blue
$TenantId = az account show --query tenantId -o tsv
Write-Host "  Tenant ID: $TenantId"

# Step 1: Create app registration
Write-Host ""
Write-Host "📝 Step 1: Creating app registration..." -ForegroundColor Blue

$AppRegistrationJson = az ad app create `
    --display-name "$AppName" `
    --web-redirect-uris "$RedirectUri" `
    --sign-in-audience "AzureADMyOrg" `
    --query "{appId:appId,objectId:id}" `
    --output json

$AppRegistration = $AppRegistrationJson | ConvertFrom-Json
$AppId = $AppRegistration.appId
$ObjectId = $AppRegistration.objectId

Write-Host "✅ App registration created" -ForegroundColor Green
Write-Host "  App ID (Client ID): $AppId"
Write-Host "  Object ID: $ObjectId"

# Step 2: Create service principal
Write-Host ""
Write-Host "🔑 Step 2: Creating service principal..." -ForegroundColor Blue

$ServicePrincipalId = az ad sp create --id $AppId --query "id" --output tsv
Write-Host "✅ Service principal created" -ForegroundColor Green
Write-Host "  Service Principal ID: $ServicePrincipalId"

# Step 3: Add required API permissions
Write-Host ""
Write-Host "🛡️  Step 3: Adding Microsoft Graph API permissions..." -ForegroundColor Blue

# Microsoft Graph API ID
$GraphApiId = "00000003-0000-0000-c000-000000000000"

# Permission IDs for Microsoft Graph
$SitesReadWriteAll = "89fe6a52-be36-487e-b7d8-d061c450a026"  # Sites.ReadWrite.All (Application)
$FilesReadWriteAll = "75359482-378d-4052-8f01-80520e7db3cd"   # Files.ReadWrite.All (Application)
$UserRead = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"           # User.Read (Delegated)

# Add application permissions
Write-Host "  Adding Sites.ReadWrite.All (Application)..."
az ad app permission add --id $AppId --api $GraphApiId --api-permissions "$SitesReadWriteAll=Role"

Write-Host "  Adding Files.ReadWrite.All (Application)..."
az ad app permission add --id $AppId --api $GraphApiId --api-permissions "$FilesReadWriteAll=Role"

Write-Host "  Adding User.Read (Delegated)..."
az ad app permission add --id $AppId --api $GraphApiId --api-permissions "$UserRead=Scope"

Write-Host "✅ API permissions added" -ForegroundColor Green

# Step 4: Grant admin consent (with retry logic)
Write-Host ""
Write-Host "🔓 Step 4: Granting admin consent..." -ForegroundColor Blue

# Wait longer for permissions to propagate
Write-Host "  Waiting for permissions to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

$ConsentAttempts = 0
$MaxConsentAttempts = 3
$ConsentSuccess = $false

while ($ConsentAttempts -lt $MaxConsentAttempts -and -not $ConsentSuccess) {
    $ConsentAttempts++
    Write-Host "  Consent attempt $ConsentAttempts of $MaxConsentAttempts..." -ForegroundColor Yellow
    
    try {
        az ad app permission admin-consent --id $AppId 2>$null
        $ConsentSuccess = $true
        Write-Host "✅ Admin consent granted" -ForegroundColor Green
    } catch {
        if ($ConsentAttempts -lt $MaxConsentAttempts) {
            Write-Host "  Consent failed, waiting 10 seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        } else {
            Write-Host "⚠️  Admin consent failed after $MaxConsentAttempts attempts" -ForegroundColor Yellow
            Write-Host "  You can grant consent manually in Azure Portal:" -ForegroundColor Yellow
            Write-Host "  1. Go to Azure Portal > Azure Active Directory > App registrations" -ForegroundColor Yellow
            Write-Host "  2. Find '$AppName' app" -ForegroundColor Yellow
            Write-Host "  3. Go to API permissions" -ForegroundColor Yellow
            Write-Host "  4. Click 'Grant admin consent for Charleston School of Law'" -ForegroundColor Yellow
        }
    }
}

# Step 5: Create client secret
Write-Host ""
Write-Host "🔐 Step 5: Creating client secret..." -ForegroundColor Blue

$SecretName = "ExamSoft-Formatter-Secret"
$SecretExpiry = "2026-12-31"  # 2+ years from now

$ClientSecret = az ad app credential reset `
    --id $AppId `
    --display-name "$SecretName" `
    --end-date "$SecretExpiry" `
    --query "password" `
    --output tsv

Write-Host "✅ Client secret created" -ForegroundColor Green
Write-Host "⚠️  IMPORTANT: Save this client secret - it won't be shown again!" -ForegroundColor Yellow

# Step 6: Generate configuration
Write-Host ""
Write-Host "📄 Step 6: Generating application configuration..." -ForegroundColor Blue

$ConfigContent = @"
# ExamSoft Formatter - Microsoft 365 Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
# 
# SECURITY NOTE: Keep the client_secret secure and do not commit to version control

M365_CONFIG = {
    "client_id": "$AppId",
    "client_secret": "$ClientSecret",  # KEEP THIS SECURE!
    "tenant_id": "$TenantDomain",
    "authority": "https://login.microsoftonline.com/$TenantDomain",
    "scope": [
        "https://graph.microsoft.com/Sites.ReadWrite.All", 
        "https://graph.microsoft.com/Files.ReadWrite.All",
        "https://graph.microsoft.com/User.Read"
    ],
    "redirect_uri": "$RedirectUri"
}

# Azure AD App Registration Details
APP_REGISTRATION_INFO = {
    "app_name": "$AppName",
    "app_id": "$AppId", 
    "object_id": "$ObjectId",
    "tenant_id": "$TenantId",
    "service_principal_id": "$ServicePrincipalId",
    "created_date": "$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")"
}
"@

$ConfigContent | Out-File -FilePath "examsoft_m365_config.py" -Encoding UTF8

Write-Host "✅ Configuration file created: examsoft_m365_config.py" -ForegroundColor Green

# Step 7: Summary and next steps
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Blue
Write-Host "  App Name: $AppName"
Write-Host "  Client ID: $AppId"
Write-Host "  Tenant: $TenantDomain"
Write-Host "  Secret Expires: $SecretExpiry"
Write-Host ""
Write-Host "📁 Files Created:" -ForegroundColor Blue
Write-Host "  📄 examsoft_m365_config.py - Configuration for your application"
Write-Host ""
Write-Host "⚠️  SECURITY REMINDERS:" -ForegroundColor Yellow
Write-Host "  🔐 Keep the client secret secure"
Write-Host "  📝 Do not commit secrets to version control"
Write-Host "  🔄 Set up secret rotation before expiry ($SecretExpiry)"
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Blue
Write-Host "  1. Copy the configuration from examsoft_m365_config.py"
Write-Host "  2. Update M365_CONFIG in examsoft_formatter_updated.py"
Write-Host "  3. Test the SharePoint integration"
Write-Host "  4. Deploy to your users"
Write-Host ""
Write-Host "✅ ExamSoft Formatter SharePoint integration is ready!" -ForegroundColor Green

# Display the client secret one more time for emphasis
Write-Host ""
Write-Host "🔑 CLIENT SECRET (save this now!):" -ForegroundColor Red -BackgroundColor Yellow
Write-Host $ClientSecret -ForegroundColor Black -BackgroundColor Yellow
Write-Host ""
