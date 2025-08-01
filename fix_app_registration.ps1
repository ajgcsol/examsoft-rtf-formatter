# Fix Azure AD App Registration for Device Code Flow
# This script configures the app for public client authentication

$appId = "4848a7e9-327a-49ff-a789-6f8b928615b7"

Write-Host "Configuring Azure AD app for device code flow..."

# Enable public client
az ad app update --id $appId --is-fallback-public-client true

# Create a manifest to clear web redirect URIs
$manifest = @{
    "web" = @{
        "redirectUris" = @()
        "implicitGrantSettings" = @{
            "enableAccessTokenIssuance" = $false
            "enableIdTokenIssuance" = $false
        }
    }
} | ConvertTo-Json -Depth 10

$manifestFile = "app_manifest.json"
$manifest | Out-File -FilePath $manifestFile -Encoding UTF8

# Update the app with the manifest
az ad app update --id $appId --web @$manifestFile

# Clean up
Remove-Item $manifestFile

Write-Host "App registration updated for device code flow"
Write-Host "Web redirect URIs cleared"
Write-Host "Public client enabled"
