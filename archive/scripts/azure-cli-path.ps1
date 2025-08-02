# Azure CLI PATH Configuration Script
# Simple script to add Azure CLI to PATH without special characters

Write-Host "Configuring Azure CLI PATH..."

# Common Azure CLI installation paths
$possiblePaths = @(
    "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:LocalAppData}\Programs\Azure CLI\wbin",
    "${env:ProgramData}\chocolatey\lib\azure-cli\tools\cli"
)

$azCliPath = $null

# Find Azure CLI installation
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\az.cmd") {
        $azCliPath = $path
        Write-Host "Found Azure CLI at: $path"
        break
    }
}

if (-not $azCliPath) {
    Write-Host "Azure CLI not found. Please install it first."
    Write-Host "Download from: https://aka.ms/installazurecliwindows"
    exit 1
}

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")

# Check if already in PATH
if ($currentPath -split ';' -contains $azCliPath) {
    Write-Host "Azure CLI is already in system PATH"
} else {
    try {
        # Add to system PATH
        $newPath = "$currentPath;$azCliPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
        Write-Host "Added Azure CLI to system PATH"
    } catch {
        Write-Host "Failed to update system PATH. Try running as administrator."
        Write-Host "Error: $($_.Exception.Message)"
    }
}

# Add to current session PATH
$env:PATH = "$env:PATH;$azCliPath"
Write-Host "Added Azure CLI to current session PATH"

# Test Azure CLI
Write-Host "Testing Azure CLI..."
try {
    $version = az --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Azure CLI is working!"
        Write-Host "Version info:"
        az --version
    } else {
        Write-Host "Azure CLI test failed"
    }
} catch {
    Write-Host "Error testing Azure CLI: $($_.Exception.Message)"
}

Write-Host "PATH configuration complete!"
