@echo off
REM Add Azure CLI to PATH - Batch Script
REM This script doesn't require execution policy changes

echo =====================================
echo Adding Azure CLI to System PATH
echo =====================================

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: This script requires Administrator privileges
    echo Please run Command Prompt as Administrator
    pause
    exit /b 1
)

echo ✅ Running with Administrator privileges

REM Common Azure CLI paths
set "AZPATH1=%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin"
set "AZPATH2=%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
set "AZPATH3=%LOCALAPPDATA%\Programs\Microsoft\Azure CLI\wbin"

REM Check for Azure CLI installation
if exist "%AZPATH1%\az.cmd" (
    set "AZPATH=%AZPATH1%"
    goto :found
)

if exist "%AZPATH2%\az.cmd" (
    set "AZPATH=%AZPATH2%"
    goto :found
)

if exist "%AZPATH3%\az.cmd" (
    set "AZPATH=%AZPATH3%"
    goto :found
)

echo ❌ Azure CLI not found in common locations
echo Please install Azure CLI first:
echo 1. Download from: https://aka.ms/installazurecliwindows
echo 2. Or run: winget install Microsoft.AzureCLI
pause
exit /b 1

:found
echo ✅ Found Azure CLI at: %AZPATH%

REM Check if already in PATH
echo %PATH% | findstr /i "%AZPATH%" >nul
if %errorlevel% equ 0 (
    echo ✅ Azure CLI is already in system PATH
    goto :test
)

REM Add to system PATH
echo Adding Azure CLI to system PATH...
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSPATH=%%b"
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "%SYSPATH%;%AZPATH%" /f >nul

if %errorlevel% equ 0 (
    echo ✅ Azure CLI successfully added to system PATH
) else (
    echo ❌ Failed to update system PATH
    pause
    exit /b 1
)

:test
echo.
echo 🧪 Testing Azure CLI...
"%AZPATH%\az.cmd" --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Azure CLI is working!
    "%AZPATH%\az.cmd" --version | findstr "azure-cli"
) else (
    echo ⚠️  Azure CLI test failed. You may need to restart your terminal.
)

echo.
echo 📋 Summary:
echo ✅ Azure CLI Path: %AZPATH%
echo ✅ Added to System PATH: Yes
echo.
echo 🎯 Next Steps:
echo 1. Close and reopen your terminal/PowerShell
echo 2. Test with: az --version
echo 3. Login with: az login
echo 4. Run deployment: .\deploy-to-azure.ps1
echo.
echo ✨ Azure CLI PATH configuration completed!
pause
