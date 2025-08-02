# PowerShell script to update Azure AD app registration redirect URI
# Run this script to add the correct redirect URI for Streamlit

Write-Host "Updating Azure AD App Registration for ExamSoft Formatter..." -ForegroundColor Green

# App details
$appId = "4848a7e9-327a-49ff-a789-6f8b928615b7"
$newRedirectUri = "http://localhost:8503"

try {
    # Check if logged in
    $context = az account show 2>$null
    if (!$context) {
        Write-Host "Please log in to Azure CLI first..." -ForegroundColor Yellow
        az login
    }

    Write-Host "Getting current app registration..." -ForegroundColor Yellow
    $app = az ad app show --id $appId | ConvertFrom-Json

    # Get current redirect URIs
    $currentUris = @()
    if ($app.web.redirectUris) {
        $currentUris = $app.web.redirectUris
    }

    # Add new URI if not already present
    if ($newRedirectUri -notin $currentUris) {
        $currentUris += $newRedirectUri
        Write-Host "Adding redirect URI: $newRedirectUri" -ForegroundColor Yellow
        
        # Update the app registration
        $uriList = $currentUris -join " "
        az ad app update --id $appId --web-redirect-uris $currentUris
        
        Write-Host "Successfully updated redirect URIs!" -ForegroundColor Green
        Write-Host "Current redirect URIs:" -ForegroundColor Cyan
        foreach ($uri in $currentUris) {
            Write-Host "  - $uri" -ForegroundColor White
        }
    } else {
        Write-Host "Redirect URI $newRedirectUri already exists." -ForegroundColor Green
    }

    Write-Host "`nApp registration update complete!" -ForegroundColor Green
    Write-Host "You can now use the SharePoint integration with the updated redirect URI." -ForegroundColor Green

} catch {
    Write-Host "Error updating app registration: $_" -ForegroundColor Red
    Write-Host "Please ensure you have the necessary permissions to modify app registrations." -ForegroundColor Yellow
}
