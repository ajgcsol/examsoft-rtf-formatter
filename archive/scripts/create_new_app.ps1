# Create a new Azure AD App Registration specifically for Device Code Flow
# This ensures clean configuration without any confidential client settings

Write-Host "Creating new Azure AD app registration for device code flow..."

# Create new app registration
$appName = "ExamSoft Formatter Device Flow"
$appResult = az ad app create --display-name $appName --is-fallback-public-client true --query "{appId:appId, displayName:displayName}" -o json | ConvertFrom-Json

Write-Host "Created new app: $($appResult.displayName)"
Write-Host "App ID: $($appResult.appId)"

# Add required Microsoft Graph permissions
$graphPermissions = @(
    "https://graph.microsoft.com/Sites.ReadWrite.All",
    "https://graph.microsoft.com/Files.ReadWrite.All",
    "https://graph.microsoft.com/User.Read"
)

foreach ($permission in $graphPermissions) {
    Write-Host "Adding permission: $permission"
    az ad app permission add --id $appResult.appId --api 00000003-0000-0000-c000-000000000000 --api-permissions $(
        switch ($permission) {
            "https://graph.microsoft.com/Sites.ReadWrite.All" { "9492366f-7969-46a4-8d15-ed1a20078fff=Scope" }
            "https://graph.microsoft.com/Files.ReadWrite.All" { "75359482-378d-4052-8f01-80520e7db3cd=Scope" }
            "https://graph.microsoft.com/User.Read" { "e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope" }
        }
    )
}

Write-Host ""
Write-Host "New App Registration Details:"
Write-Host "App ID: $($appResult.appId)"
Write-Host "Name: $($appResult.displayName)"
Write-Host "Public Client: Yes (Device Code Flow Enabled)"
Write-Host ""
Write-Host "Update your examsoft_m365_config.py with this App ID:"
Write-Host "client_id: '$($appResult.appId)'"
