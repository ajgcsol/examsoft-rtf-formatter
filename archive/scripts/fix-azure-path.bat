@echo off
echo Adding Azure CLI to system PATH...

REM Check for Azure CLI in common locations and add to system PATH
if exist "%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
    echo Found Azure CLI at: "%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin"
    setx PATH "%PATH%;%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin" /M
    echo Added to system PATH
) else if exist "%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
    echo Found Azure CLI at: "%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin"
    setx PATH "%PATH%;%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin" /M
    echo Added to system PATH
) else if exist "%LocalAppData%\Programs\Azure CLI\wbin\az.cmd" (
    echo Found Azure CLI at: "%LocalAppData%\Programs\Azure CLI\wbin"
    setx PATH "%PATH%;%LocalAppData%\Programs\Azure CLI\wbin" /M
    echo Added to system PATH
) else (
    echo Azure CLI not found. Please install it first.
    echo Download from: https://aka.ms/installazurecliwindows
)

echo.
echo NOTE: You may need to restart your command prompt for changes to take effect.
pause
