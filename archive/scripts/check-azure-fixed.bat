@echo off
setlocal enabledelayedexpansion

echo ================================================
echo Azure CLI Test and Configuration  
echo ================================================
echo.

echo Testing Azure CLI availability...

REM First try to find az command directly
where az >nul 2>&1
if !errorlevel! == 0 (
    echo ✅ Azure CLI found in PATH
    echo.
    echo Getting version info...
    az --version
    echo.
    echo Testing login status...
    az account show --output table >nul 2>&1
    if !errorlevel! == 0 (
        echo ✅ Already logged into Azure
    ) else (
        echo ⚠️  Not logged into Azure
        echo Run: az login
    )
    goto :end
)

echo ❌ Azure CLI not found in PATH
echo.
echo Checking common installation locations...

REM Define search paths
set "path1=%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
set "path2=%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin" 
set "path3=%LocalAppData%\Programs\Azure CLI\wbin"

REM Check each path
if exist "!path1!\az.cmd" (
    echo ✅ Found Azure CLI at: "!path1!"
    echo Adding to PATH for this session...
    set "PATH=%PATH%;!path1!"
    echo Testing...
    "!path1!\az.cmd" --version
    goto :end
)

if exist "!path2!\az.cmd" (
    echo ✅ Found Azure CLI at: "!path2!"
    echo Adding to PATH for this session...
    set "PATH=%PATH%;!path2!"
    echo Testing...
    "!path2!\az.cmd" --version
    goto :end
)

if exist "!path3!\az.cmd" (
    echo ✅ Found Azure CLI at: "!path3!"
    echo Adding to PATH for this session...
    set "PATH=%PATH%;!path3!"
    echo Testing...
    "!path3!\az.cmd" --version
    goto :end
)

echo ❌ Azure CLI not found in any common location
echo.
echo Please install Azure CLI from:
echo https://aka.ms/installazurecliwindows
echo.
echo After installation, restart this script

:end
echo.
echo ================================================
echo Next Steps:
echo 1. If Azure CLI is working, run: az login
echo 2. Set subscription: az account set --subscription "YourSubscription"  
echo 3. Deploy to Azure: PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1
echo ================================================
echo.
pause
