@echo off
echo Updating Azure Container with fixed port configuration...
echo.

REM Get the existing ACR name from azure_config.json
for /f "tokens=2 delims=:" %%a in ('findstr "acr_name" azure_config.json') do (
    set "acrname=%%a"
)
REM Clean up the ACR name (remove quotes and spaces)
set "acrname=%acrname:"=%"
set "acrname=%acrname: =%"
set "acrname=%acrname:,=%"

echo Found ACR: %acrname%
echo.

echo Step 1: Login to ACR
az acr login --name %acrname%

echo.
echo Step 2: Build new Docker image
docker build -t %acrname%.azurecr.io/libreoffice-converter:latest .

echo.
echo Step 3: Push updated image to ACR
docker push %acrname%.azurecr.io/libreoffice-converter:latest

echo.
echo Step 4: Restart Azure Container Instance
az container restart --resource-group CSOLIT --name examsoft-converter

echo.
echo Step 5: Wait for container to start (30 seconds)
timeout /t 30 /nobreak

echo.
echo Step 6: Test the health endpoint
curl http://4.157.121.65:5000/health

echo.
echo Update complete! Container should now be running on port 5000.
pause
