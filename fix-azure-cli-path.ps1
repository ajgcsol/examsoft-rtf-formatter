# Add Azure CLI to PATH - Simple PowerShell Script
# Run this as Administrator

param(
    [switch]$Verbose = $false
)

# Simple output functions without emoji
function Write-Success { 
    param($Message) 
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green 
}

function Write-Info { 
    param($Message) 
    Write-Host "[INFO] $Message" -ForegroundColor Cyan 
}

function Write-Warning { 
    param($Message) 
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow 
}

function Write-Error { 
    param($Message) 
    Write-Host "[ERROR] $Message" -ForegroundColor Red 
}

Write-Info "Adding Azure CLI to System PATH"
Write-Info "================================"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "This script requires Administrator privileges"
    Write-Info "Please run PowerShell as Administrator and try again"
    exit 1
}

# Common Azure CLI installation paths
$azurePaths = @(
    "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:LOCALAPPDATA}\Programs\Microsoft\Azure CLI\wbin"
)

# Find Azure CLI installation
$azPath = $null
foreach ($path in $azurePaths) {
    $azExe = Join-Path $path "az.cmd"
    if (Test-Path $azExe) {
        $azPath = $path
        Write-Success "Found Azure CLI at: $azPath"
        break
    }
}

if (-not $azPath) {
    Write-Error "Azure CLI installation not found!"
    Write-Info "Common installation paths checked:"
    foreach ($path in $azurePaths) {
        Write-Info "  - $path"
    }
    Write-Info ""
    Write-Info "Please install Azure CLI first:"
    Write-Info "1. Download from: https://aka.ms/installazurecliwindows"
    Write-Info "2. Or run: winget install Microsoft.AzureCLI"
    exit 1
}

# Get current system PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Check if Azure CLI path is already in PATH
if ($currentPath -like "*$azPath*") {
    Write-Success "Azure CLI is already in system PATH"
    Write-Info "Current PATH includes: $azPath"
} else {
    # Add Azure CLI to system PATH
    Write-Info "Adding Azure CLI to system PATH..."
    $newPath = $currentPath + ";" + $azPath
    
    try {
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Success "Azure CLI successfully added to system PATH"
        Write-Success "Added path: $azPath"
    } catch {
        Write-Error "Failed to update system PATH: $($_.Exception.Message)"
        exit 1
    }
}

# Update current session PATH
$env:Path = $env:Path + ";" + $azPath

# Test Azure CLI
Write-Info "Testing Azure CLI..."
try {
    $testCommand = "$azPath\az.cmd"
    $azVersion = & $testCommand --version 2>$null
    if ($azVersion) {
        Write-Success "Azure CLI is working!"
        if ($Verbose) {
            Write-Info "Version information:"
            $azVersion | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
    } else {
        throw "Azure CLI test failed"
    }
} catch {
    Write-Warning "Azure CLI test failed. You may need to restart your terminal."
}

Write-Info ""
Write-Info "Summary:"
Write-Success "Azure CLI Path: $azPath"
Write-Success "Added to System PATH: Yes"
Write-Success "Current Session Updated: Yes"

Write-Info ""
Write-Info "Next Steps:"
Write-Info "1. Close and reopen your terminal/PowerShell"
Write-Info "2. Test with: az --version"
Write-Info "3. Login with: az login"
Write-Info "4. Run deployment: .\deploy-to-azure.ps1"

Write-Success "Azure CLI PATH configuration completed!"
