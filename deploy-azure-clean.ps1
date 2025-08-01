# Azure Container Deployment Script for ExamSoft LibreOffice Converter
# This script deploys the Docker container to Azure Container Registry and Azure Container Instance

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "CSOLIT",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$AcrName = "examsoftacr$(Get-Random -Minimum 1000 -Maximum 9999)",
    
    [Parameter(Mandatory=$false)]
    [string]$AciName = "examsoft-converter",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "libreoffice-converter",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageTag = "latest"
)

# Color functions for output
function Write-Success { param($Message) Write-Host "SUCCESS: $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "INFO: $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "WARNING: $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "ERROR: $Message" -ForegroundColor Red }

Write-Info "Starting Azure Container Deployment for ExamSoft LibreOffice Converter"
Write-Info "=================================================="

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    if ($azVersion) {
        Write-Success "Azure CLI detected: $($azVersion.'azure-cli')"
    } else {
        throw "Azure CLI not found"
    }
} catch {
    Write-Error "Azure CLI is not installed or not in PATH"
    Write-Info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if Docker is installed and running
try {
    $dockerVersion = docker version --format '{{.Server.Version}}' 2>$null
    if ($dockerVersion) {
        Write-Success "Docker detected: $dockerVersion"
    } else {
        throw "Docker not found or not running"
    }
} catch {
    Write-Error "Docker is not installed or not running"
    Write-Info "Please install Docker Desktop and ensure it's running"
    exit 1
}

# Check if user is logged into Azure
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
    Write-Info "Subscription: $($account.name)"
} catch {
    Write-Error "Not logged into Azure"
    Write-Info "Please run: az login"
    exit 1
}

# Check if Dockerfile exists
if (-not (Test-Path "Dockerfile")) {
    Write-Error "Dockerfile not found in current directory"
    exit 1
}

Write-Success "All prerequisites satisfied"
Write-Info "=================================================="

# Create or use existing resource group
Write-Info "Setting up resource group: $ResourceGroupName"
$rgExists = az group exists --name $ResourceGroupName --output tsv
if ($rgExists -eq "true") {
    Write-Success "Resource group '$ResourceGroupName' already exists"
} else {
    Write-Info "Creating resource group '$ResourceGroupName' in $Location"
    az group create --name $ResourceGroupName --location $Location --output none
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Resource group created successfully"
    } else {
        Write-Error "Failed to create resource group"
        exit 1
    }
}

# Create Azure Container Registry
Write-Info "Creating Azure Container Registry: $AcrName"
$acrExists = az acr show --name $AcrName --resource-group $ResourceGroupName --output none 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "ACR '$AcrName' already exists"
} else {
    Write-Info "Creating new ACR: $AcrName"
    az acr create --resource-group $ResourceGroupName --name $AcrName --sku Basic --admin-enabled true --output none
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ACR created successfully"
    } else {
        Write-Error "Failed to create ACR"
        exit 1
    }
}

# Get ACR login server
$acrLoginServer = az acr show --name $AcrName --resource-group $ResourceGroupName --query loginServer --output tsv
Write-Info "ACR Login Server: $acrLoginServer"

# Login to ACR
Write-Info "Logging into Azure Container Registry"
az acr login --name $AcrName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login to ACR"
    exit 1
}

# Build Docker image
$fullImageName = "$acrLoginServer/$ImageName`:$ImageTag"
Write-Info "Building Docker image: $fullImageName"
docker build --no-cache -t $fullImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}
Write-Success "Docker image built successfully"

# Push image to ACR
Write-Info "Pushing image to Azure Container Registry"
docker push $fullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to push image to ACR"
    exit 1
}
Write-Success "Image pushed to ACR successfully"

# Get ACR credentials
Write-Info "Getting ACR credentials"
$acrCredentials = az acr credential show --name $AcrName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
$acrUsername = $acrCredentials.username
$acrPassword = $acrCredentials.passwords[0].value

# Create Azure Container Instance
Write-Info "Creating Azure Container Instance: $AciName"
$aciExists = az container show --name $AciName --resource-group $ResourceGroupName --output none 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Warning "ACI '$AciName' already exists, deleting and recreating"
    az container delete --name $AciName --resource-group $ResourceGroupName --yes --output none
}

Write-Info "Deploying container to Azure Container Instance"
az container create `
    --resource-group $ResourceGroupName `
    --name $AciName `
    --image $fullImageName `
    --registry-login-server $acrLoginServer `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
    --dns-name-label $AciName `
    --ports 5000 `
    --cpu 1 `
    --memory 1.5 `
    --os-type Linux `
    --restart-policy Always `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create Azure Container Instance"
    exit 1
}

Write-Success "Container Instance created successfully"

# Get the public IP and FQDN
Write-Info "Getting container instance details"
$containerDetails = az container show --name $AciName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
$publicIP = $containerDetails.ipAddress.ip
$fqdn = $containerDetails.ipAddress.fqdn

Write-Success "Container deployed successfully!"
Write-Info "=================================================="
Write-Info "Deployment Details:"
Write-Info "Resource Group: $ResourceGroupName"
Write-Info "Container Registry: $AcrName"
Write-Info "Container Instance: $AciName"
Write-Info "Public IP: $publicIP"
Write-Info "FQDN: $fqdn"
Write-Info "API Endpoint: http://$publicIP`:5000"
Write-Info "Health Check: http://$publicIP`:5000/health"
Write-Info "=================================================="

# Create configuration file for Streamlit app
Write-Info "Creating Azure configuration file"
$config = @{
    azure_endpoint = "http://$publicIP`:5000"
    resource_group = $ResourceGroupName
    container_name = $AciName
    acr_name = $AcrName
    deployment_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    status = "deployed"
} | ConvertTo-Json -Depth 3

$config | Out-File -FilePath "azure_config.json" -Encoding UTF8
Write-Success "Configuration saved to azure_config.json"

# Test the endpoint
Write-Info "Testing the deployed endpoint"
try {
    $response = Invoke-WebRequest -Uri "http://$publicIP`:5000/health" -TimeoutSec 30 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Success "Endpoint is responding correctly!"
        Write-Success "LibreOffice converter is ready for use"
    } else {
        Write-Warning "Endpoint responded with status: $($response.StatusCode)"
    }
} catch {
    Write-Warning "Could not test endpoint immediately (container may still be starting)"
    Write-Info "Please wait 2-3 minutes and test manually: http://$publicIP`:5000/health"
}

Write-Success "Deployment completed successfully!"
Write-Info "=================================================="
Write-Info "Next Steps:"
Write-Info "1. Test the API: http://$publicIP`:5000/health"
Write-Info "2. Run your Streamlit app - it will automatically detect the Azure endpoint"
Write-Info "3. Upload RTF files through the Streamlit interface"
Write-Info "4. Monitor costs in Azure portal"
Write-Info "=================================================="
Write-Info "Estimated monthly cost: 15-25 USD"
Write-Info "To cleanup resources: az group delete --name $ResourceGroupName --yes --no-wait"

Read-Host "Press Enter to finish"
