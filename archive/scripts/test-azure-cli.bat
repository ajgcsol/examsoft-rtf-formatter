@echo off
echo Testing Azure CLI availability...
where az
if %errorlevel% == 0 (
    echo Azure CLI found!
    az --version
) else (
    echo Azure CLI not found in PATH
    echo Checking common installation locations...
    
    if exist "%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
        echo Found Azure CLI at: %ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin
        set PATH=%PATH%;%ProgramFiles%\Microsoft SDKs\Azure\CLI2\wbin
        echo Added to PATH for this session
        az --version
    ) else if exist "%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
        echo Found Azure CLI at: %ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin
        set PATH=%PATH%;%ProgramFiles(x86)%\Microsoft SDKs\Azure\CLI2\wbin
        echo Added to PATH for this session
        az --version
    ) else if exist "%LocalAppData%\Programs\Azure CLI\wbin\az.cmd" (
        echo Found Azure CLI at: %LocalAppData%\Programs\Azure CLI\wbin
        set PATH=%PATH%;%LocalAppData%\Programs\Azure CLI\wbin
        echo Added to PATH for this session
        az --version
    ) else (
        echo Azure CLI not found. Please install it from:
        echo https://aka.ms/installazurecliwindows
    )
)
pause
