# Azure CLI Status Check - Simple Version
Write-Host "Checking Azure CLI Status..." -ForegroundColor Cyan
Write-Host "=================================================="

# Test if az command is available
$azAvailable = $false
try {
    $null = Get-Command az -ErrorAction Stop
    $azAvailable = $true
    Write-Host "SUCCESS: Azure CLI found in PATH" -ForegroundColor Green
    
    # Get version
    try {
        az --version
    } catch {
        Write-Host "Azure CLI is available but version check failed" -ForegroundColor Yellow
    }
    
    # Check login status
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Host "SUCCESS: Logged in as: $($account.user.name)" -ForegroundColor Green
            Write-Host "Subscription: $($account.name)" -ForegroundColor Green
        }
    } catch {
        Write-Host "WARNING: Not logged into Azure" -ForegroundColor Yellow
        Write-Host "Run: az login" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "ERROR: Azure CLI not found in PATH" -ForegroundColor Red
    
    # Check common installation locations
    $locations = @(
        "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin",
        "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin",
        "${env:LocalAppData}\Programs\Azure CLI\wbin"
    )
    
    $found = $false
    foreach ($location in $locations) {
        if (Test-Path "$location\az.cmd") {
            Write-Host "FOUND: Azure CLI at: $location" -ForegroundColor Green
            Write-Host "Adding to PATH for this session..." -ForegroundColor Cyan
            $env:PATH = "$env:PATH;$location"
            $found = $true
            $azAvailable = $true
            break
        }
    }
    
    if (-not $found) {
        Write-Host "ERROR: Azure CLI not found in common locations" -ForegroundColor Red
        Write-Host "Please install Azure CLI from:" -ForegroundColor Yellow
        Write-Host "https://aka.ms/installazurecliwindows" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "=================================================="

if ($azAvailable) {
    Write-Host "1. SUCCESS: Azure CLI is ready" -ForegroundColor Green
    
    # Check if logged in
    try {
        $null = az account show --output json 2>$null
        Write-Host "2. SUCCESS: Already logged into Azure" -ForegroundColor Green
        Write-Host "3. READY TO DEPLOY! Run:" -ForegroundColor Cyan
        Write-Host "   PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1" -ForegroundColor Yellow
    } catch {
        Write-Host "2. Login to Azure:" -ForegroundColor Yellow
        Write-Host "   az login" -ForegroundColor Cyan
        Write-Host "3. Then deploy:" -ForegroundColor Yellow
        Write-Host "   PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1" -ForegroundColor Cyan
    }
} else {
    Write-Host "1. Install Azure CLI first" -ForegroundColor Red
    Write-Host "2. Restart this script" -ForegroundColor Yellow
    Write-Host "3. Login: az login" -ForegroundColor Yellow
    Write-Host "4. Deploy: PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Expected Azure costs: approximately 15-25 USD per month" -ForegroundColor Green
Write-Host "Deployment time: approximately 5-10 minutes" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue"
