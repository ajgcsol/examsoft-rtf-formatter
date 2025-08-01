@echo off
setlocal enabledelayedexpansion

echo Adding Azure CLI to system PATH...
echo.

REM Define search paths using variables
set "path1=%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
set "path2=%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin"
set "path3=%LocalAppData%\Programs\Azure CLI\wbin"

REM Check each location
if exist "!path1!\az.cmd" (
    echo Found Azure CLI at: "!path1!"
    setx PATH "%PATH%;!path1!" /M >nul 2>&1
    if !errorlevel! == 0 (
        echo ✅ Successfully added to system PATH
    ) else (
        echo ⚠️  Failed to add to system PATH - try running as Administrator
    )
    goto :found
)

if exist "!path2!\az.cmd" (
    echo Found Azure CLI at: "!path2!"
    setx PATH "%PATH%;!path2!" /M >nul 2>&1
    if !errorlevel! == 0 (
        echo ✅ Successfully added to system PATH
    ) else (
        echo ⚠️  Failed to add to system PATH - try running as Administrator
    )
    goto :found
)

if exist "!path3!\az.cmd" (
    echo Found Azure CLI at: "!path3!"
    setx PATH "%PATH%;!path3!" /M >nul 2>&1
    if !errorlevel! == 0 (
        echo ✅ Successfully added to system PATH
    ) else (
        echo ⚠️  Failed to add to system PATH - try running as Administrator
    )
    goto :found
)

echo ❌ Azure CLI not found in common locations
echo Please install it first from: https://aka.ms/installazurecliwindows
goto :end

:found
echo.
echo ✅ Azure CLI configuration complete!
echo.
echo NOTE: You may need to restart your command prompt for changes to take effect.
echo Test with: az --version

:end
echo.
pause
