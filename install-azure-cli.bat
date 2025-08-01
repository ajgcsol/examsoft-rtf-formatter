@echo off
REM Simple Azure CLI installer for Windows
REM This script downloads and installs Azure CLI

echo =========================================
echo Azure CLI Quick Installer
echo =========================================

REM Check if Azure CLI is already installed
az --version >nul 2>&1
if %errorlevel% == 0 (
    echo Azure CLI is already installed and working!
    az --version
    echo.
    echo You can now run the Azure deployment script:
    echo   .\deploy-to-azure.ps1
    pause
    exit /b 0
)

echo Azure CLI not found. Installing...
echo.

REM Download and install using winget (Windows Package Manager)
echo Attempting installation with Windows Package Manager (winget)...
winget install Microsoft.AzureCLI --silent --accept-package-agreements --accept-source-agreements
if %errorlevel% == 0 (
    echo.
    echo Azure CLI installed successfully via winget!
    goto :test_installation
)

echo.
echo Winget installation failed. Trying MSI installer...

REM Fallback: Download MSI installer
set "download_url=https://aka.ms/installazurecliwindows"
set "installer_path=%TEMP%\AzureCLI.msi"

echo Downloading Azure CLI installer...
powershell -Command "Invoke-WebRequest -Uri '%download_url%' -OutFile '%installer_path%'"

if exist "%installer_path%" (
    echo Installing Azure CLI...
    msiexec /i "%installer_path%" /quiet /norestart
    del "%installer_path%" >nul 2>&1
) else (
    echo Failed to download Azure CLI installer.
    echo Please download manually from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
    pause
    exit /b 1
)

:test_installation
echo.
echo Testing Azure CLI installation...
echo.

REM Refresh PATH for current session
call refreshenv >nul 2>&1

REM Test Azure CLI
az --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Azure CLI is working!
    az --version
    echo.
    echo 🎯 Next steps:
    echo 1. Run: az login
    echo 2. Run: az account show
    echo 3. Run: .\deploy-to-azure.ps1
    echo.
) else (
    echo ❌ Azure CLI installation may have failed.
    echo Please restart your command prompt and try 'az --version'
    echo If that doesn't work, install manually from:
    echo https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
)

pause
