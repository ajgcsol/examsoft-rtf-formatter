# Quick Azure CLI PATH Fix - One-liner Commands
# Copy and paste these commands into PowerShell (run as Administrator)

# Method 1: Standard installation path
$azPath = "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin"
if (Test-Path "$azPath\az.cmd") {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$azPath*") {
        [Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $azPath, "Machine")
        Write-Host "✅ Azure CLI added to PATH: $azPath" -ForegroundColor Green
    } else {
        Write-Host "✅ Azure CLI already in PATH" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Azure CLI not found at standard location" -ForegroundColor Red
}

# Method 2: Alternative path
$azPath2 = "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin"
if (Test-Path "$azPath2\az.cmd") {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$azPath2*") {
        [Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $azPath2, "Machine")
        Write-Host "✅ Azure CLI added to PATH: $azPath2" -ForegroundColor Green
    }
}

# Refresh current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "🔄 Please restart your terminal and test with: az --version" -ForegroundColor Cyan
