# Azure CLI Installation and PATH Configuration Script
# This script installs Azure CLI and ensures it's properly added to PATH

param(
    [Parameter(Mandatory=$false)]
    [switch]$ForceReinstall = $false
)

# Color functions for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Info "🔧 Azure CLI Installation and PATH Configuration"
Write-Info "================================================"

# Check if Azure CLI is already installed
$azInstalled = $false
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    if ($azVersion) {
        $azInstalled = $true
        Write-Success "Azure CLI already installed: $($azVersion.'azure-cli')"
        
        if (-not $ForceReinstall) {
            Write-Info "Use -ForceReinstall flag to reinstall anyway"
            exit 0
        }
    }
} catch {
    Write-Info "Azure CLI not found or not working properly"
}

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "This script requires Administrator privileges for system-wide installation"
    Write-Info "Attempting to restart as Administrator..."
    
    # Restart script as Administrator
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$scriptPath`""
    exit
}

Write-Success "Running with Administrator privileges"

# Download and install Azure CLI using MSI installer
Write-Info "📥 Downloading Azure CLI installer..."

$downloadUrl = "https://aka.ms/installazurecliwindows"
$installerPath = "$env:TEMP\AzureCLI.msi"

try {
    # Download the installer
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    Write-Success "Azure CLI installer downloaded"
    
    # Install Azure CLI
    Write-Info "🔨 Installing Azure CLI (this may take a few minutes)..."
    Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installerPath`" /quiet /norestart"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Azure CLI installation completed"
    } else {
        throw "Installation failed with exit code: $LASTEXITCODE"
    }
    
    # Clean up installer
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
} catch {
    Write-Error "Failed to download or install Azure CLI: $($_.Exception.Message)"
    exit 1
}

# Refresh environment variables to pick up new PATH
Write-Info "🔄 Refreshing environment variables..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Common Azure CLI installation paths
$commonPaths = @(
    "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:LOCALAPPDATA}\Programs\Microsoft\Azure CLI\wbin"
)

# Check if Azure CLI is now in PATH
$azFound = $false
$azPath = ""

foreach ($path in $commonPaths) {
    $azExe = Join-Path $path "az.cmd"
    if (Test-Path $azExe) {
        $azPath = $path
        $azFound = $true
        Write-Success "Found Azure CLI at: $azPath"
        break
    }
}

if (-not $azFound) {
    # Try to find Azure CLI in other locations
    $azExe = Get-ChildItem -Path "C:\Program Files*" -Recurse -Name "az.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($azExe) {
        $azPath = Split-Path $azExe -Parent
        $azFound = $true
        Write-Success "Found Azure CLI at: $azPath"
    }
}

if ($azFound) {
    # Check if path is already in system PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    if ($currentPath -notlike "*$azPath*") {
        Write-Info "➕ Adding Azure CLI to system PATH..."
        $newPath = $currentPath + ";" + $azPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Success "Azure CLI added to system PATH"
    } else {
        Write-Success "Azure CLI already in system PATH"
    }
    
    # Update current session PATH
    $env:Path = $env:Path + ";" + $azPath
    
} else {
    Write-Error "Could not locate Azure CLI installation"
    Write-Info "You may need to manually add Azure CLI to your PATH"
    exit 1
}

# Test Azure CLI
Write-Info "🧪 Testing Azure CLI installation..."
try {
    $testResult = & "$azPath\az.cmd" version --output json 2>$null | ConvertFrom-Json
    if ($testResult) {
        Write-Success "Azure CLI is working! Version: $($testResult.'azure-cli')"
        
        # Show installation details
        Write-Info ""
        Write-Info "📋 Installation Summary:"
        Write-Success "Azure CLI Version: $($testResult.'azure-cli')"
        Write-Success "Installation Path: $azPath"
        Write-Success "Added to System PATH: Yes"
        
        Write-Info ""
        Write-Info "🎯 Next Steps:"
        Write-Info "1. Close and reopen your terminal/PowerShell"
        Write-Info "2. Run 'az login' to authenticate with Azure"
        Write-Info "3. Run 'az account show' to verify authentication"
        Write-Info "4. Now you can use the Azure deployment script!"
        
    } else {
        throw "Azure CLI test failed"
    }
} catch {
    Write-Error "Azure CLI test failed: $($_.Exception.Message)"
    Write-Info "You may need to restart your terminal and try 'az --version'"
}

Write-Info ""
Write-Success "✨ Azure CLI installation and PATH configuration completed!"
Write-Info "Please restart your terminal/PowerShell to ensure PATH changes take effect."
