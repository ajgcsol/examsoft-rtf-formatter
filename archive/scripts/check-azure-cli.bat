@echo off
echo ================================================
echo Azure CLI Test and Configuration
echo ================================================
echo.

echo Testing Azure CLI availability...
where az >nul 2>nul
if %errorlevel% == 0 (
    echo ✅ Azure CLI found in PATH
    echo.
    echo Getting version info...
    az --version
    echo.
    echo Testing login status...
    az account show --output table 2>nul
    if %errorlevel% == 0 (
        echo ✅ Already logged into Azure
    ) else (
        echo ⚠️  Not logged into Azure
        echo Run: az login
    )
) else (
    echo ❌ Azure CLI not found in PATH
    echo.
    echo Checking common installation locations...
    
    if exist "%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
        echo ✅ Found Azure CLI at: "%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
        echo Adding to PATH for this session...
        set "PATH=%PATH%;%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
        echo Testing...
        az --version
    ) else if exist "%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
        echo ✅ Found Azure CLI at: "%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin"
        echo Adding to PATH for this session...
        set "PATH=%PATH%;%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin"
        echo Testing...
        az --version
    ) else if exist "%LocalAppData%\Programs\Azure CLI\wbin\az.cmd" (
        echo ✅ Found Azure CLI at: "%LocalAppData%\Programs\Azure CLI\wbin"
        echo Adding to PATH for this session...
        set "PATH=%PATH%;%LocalAppData%\Programs\Azure CLI\wbin"
        echo Testing...
        az --version
    ) else (
        echo ❌ Azure CLI not found in any common location
        echo.
        echo Please install Azure CLI from:
        echo https://aka.ms/installazurecliwindows
        echo.
        echo After installation, restart this script
    )
)

echo.
echo ================================================
echo Next Steps:
echo 1. If Azure CLI is working, run: az login
echo 2. Set subscription: az account set --subscription "YourSubscription"
echo 3. Deploy to Azure: PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1
echo ================================================
echo.
pause
