# Quick Container Update Script
Write-Host "Rebuilding and redeploying Azure container with updated code..." -ForegroundColor Cyan

# Get ACR name from config
$config = Get-Content "azure_config.json" | ConvertFrom-Json
$acrName = $config.acr_name
$resourceGroup = $config.resource_group
$containerName = $config.container_name

Write-Host "Using ACR: $acrName" -ForegroundColor Yellow

# Login to ACR
Write-Host "Logging into ACR..." -ForegroundColor Cyan
az acr login --name $acrName

# Build new image with updated code
$imageName = "$acrName.azurecr.io/libreoffice-converter:latest"
Write-Host "Building image: $imageName" -ForegroundColor Cyan
docker build --no-cache -t $imageName .

# Push updated image
Write-Host "Pushing updated image..." -ForegroundColor Cyan
docker push $imageName

# Restart container to use new image
Write-Host "Restarting container..." -ForegroundColor Cyan
az container restart --resource-group $resourceGroup --name $containerName

Write-Host "Update complete! Waiting 30 seconds for container to restart..." -ForegroundColor Green
Start-Sleep -Seconds 30

# Test endpoint
Write-Host "Testing endpoint..." -ForegroundColor Cyan
$endpoint = $config.azure_endpoint
try {
    $response = Invoke-WebRequest -Uri "$endpoint/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "SUCCESS: Endpoint is responding! Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Endpoint not ready yet. Wait a minute and test manually:" -ForegroundColor Yellow
    Write-Host "curl $endpoint/health" -ForegroundColor Cyan
}

Write-Host "Container update complete!" -ForegroundColor Green
