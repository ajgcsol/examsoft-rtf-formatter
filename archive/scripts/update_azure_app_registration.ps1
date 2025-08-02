# PowerShell script to update Azure AD App Registration for Streamlit Cloud
# Run this in Azure Cloud Shell or with Azure PowerShell module

# Connect to Azure AD (if not already connected)
# Connect-AzureAD

# App Registration details
$AppId = "4848a7e9-327a-49ff-a789-6f8b928615b7"
$ObjectId = "20d20db1-5ad9-49aa-a372-7102f92bd94d"

Write-Host "Updating Azure AD App Registration: $AppId" -ForegroundColor Green

# Update redirect URIs for public client
$RedirectUris = @(
    "http://localhost:8501",
    "https://csol-examsoft-converter.streamlit.app",
    "https://login.microsoftonline.com/common/oauth2/nativeclient"
)

try {
    # Get the current app registration
    $App = Get-AzureADApplication -ObjectId $ObjectId
    
    # Update public client settings
    $App.PublicClient = $true
    $App.ReplyUrls = $RedirectUris
    
    # Apply updates
    Set-AzureADApplication -ObjectId $ObjectId -PublicClient $true -ReplyUrls $RedirectUris
    
    Write-Host "✅ Successfully updated app registration!" -ForegroundColor Green
    Write-Host "Redirect URIs updated:" -ForegroundColor Yellow
    foreach ($uri in $RedirectUris) {
        Write-Host "  - $uri" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "⚠️  Please also verify API permissions and grant admin consent:" -ForegroundColor Yellow
    Write-Host "- Sites.ReadWrite.All" -ForegroundColor White
    Write-Host "- Files.ReadWrite.All" -ForegroundColor White  
    Write-Host "- User.Read" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error updating app registration: $_.Exception.Message" -ForegroundColor Red
    Write-Host "Please update manually via Azure Portal" -ForegroundColor Yellow
}
