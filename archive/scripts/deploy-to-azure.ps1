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
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Info "🚀 Starting Azure Container Deployment for ExamSoft LibreOffice Converter"
Write-Info "=================================================="

# Check if Azure CLI is installed
try {
    $azVersion = az version --output tsv --query '"azure-cli"' 2>$null
    if ($azVersion) {
        Write-Success "Azure CLI detected: $azVersion"
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
        Write-Success "Docker detected and running: $dockerVersion"
    } else {
        throw "Docker not running"
    }
} catch {
    Write-Error "Docker is not installed or not running"
    Write-Info "Please install Docker Desktop and ensure it's running"
    exit 1
}

# Check if Dockerfile exists
if (!(Test-Path "Dockerfile")) {
    Write-Error "Dockerfile not found in current directory"
    Write-Info "Please run this script from the exam-formatter directory"
    exit 1
}

Write-Success "All prerequisites verified"

# Step 1: Login to Azure (if not already logged in)
Write-Info "🔐 Checking Azure authentication..."
try {
    $currentAccount = az account show --query "user.name" --output tsv 2>$null
    if ($currentAccount) {
        Write-Success "Already authenticated as: $currentAccount"
    } else {
        throw "Not authenticated"
    }
} catch {
    Write-Info "Please authenticate with Azure..."
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Azure authentication failed"
        exit 1
    }
}

# Step 2: Create Resource Group
Write-Info "📁 Creating resource group: $ResourceGroupName"
az group create --name $ResourceGroupName --location $Location --output table
if ($LASTEXITCODE -eq 0) {
    Write-Success "Resource group created/verified: $ResourceGroupName"
} else {
    Write-Error "Failed to create resource group"
    exit 1
}

# Step 3: Create Azure Container Registry
Write-Info "🏗️  Creating Azure Container Registry: $AcrName"
az acr create --resource-group $ResourceGroupName --name $AcrName --sku Basic --admin-enabled true --output table
if ($LASTEXITCODE -eq 0) {
    Write-Success "ACR created: $AcrName"
} else {
    Write-Warning "ACR creation failed or already exists, continuing..."
}

# Step 4: Get ACR login server
Write-Info "🔍 Getting ACR login server..."
$acrLoginServer = az acr show --name $AcrName --resource-group $ResourceGroupName --query "loginServer" --output tsv
if ($acrLoginServer) {
    Write-Success "ACR Login Server: $acrLoginServer"
} else {
    Write-Error "Failed to get ACR login server"
    exit 1
}

# Step 5: Login to ACR
Write-Info "🔐 Logging into Azure Container Registry..."
az acr login --name $AcrName
if ($LASTEXITCODE -eq 0) {
    Write-Success "Successfully logged into ACR: $AcrName"
} else {
    Write-Error "Failed to login to ACR"
    exit 1
}

# Step 6: Build and tag Docker image
Write-Info "🔨 Building Docker image: $ImageName"
$fullImageName = "$acrLoginServer/${ImageName}:${ImageTag}"
docker build -t $fullImageName .
if ($LASTEXITCODE -eq 0) {
    Write-Success "Docker image built: $fullImageName"
} else {
    Write-Error "Docker build failed"
    exit 1
}

# Step 7: Push image to ACR
Write-Info "📤 Pushing image to Azure Container Registry..."
docker push $fullImageName
if ($LASTEXITCODE -eq 0) {
    Write-Success "Image pushed to ACR: $fullImageName"
} else {
    Write-Error "Failed to push image to ACR"
    exit 1
}

# Step 8: Get ACR credentials for ACI
Write-Info "🔑 Getting ACR credentials..."
$acrUsername = az acr credential show --name $AcrName --query "username" --output tsv
$acrPassword = az acr credential show --name $AcrName --query "passwords[0].value" --output tsv

if ($acrUsername -and $acrPassword) {
    Write-Success "ACR credentials retrieved"
} else {
    Write-Error "Failed to get ACR credentials"
    exit 1
}

# Step 9: Create Azure Container Instance
Write-Info "🚀 Creating Azure Container Instance: $AciName"
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
    --memory 2 `
    --restart-policy Always `
    --output table

if ($LASTEXITCODE -eq 0) {
    Write-Success "Azure Container Instance created: $AciName"
} else {
    Write-Error "Failed to create Azure Container Instance"
    exit 1
}

# Step 10: Get ACI public endpoint
Write-Info "🌐 Getting ACI public endpoint..."
$aciState = az container show --name $AciName --resource-group $ResourceGroupName --query "instanceView.state" --output tsv
$aciFqdn = az container show --name $AciName --resource-group $ResourceGroupName --query "ipAddress.fqdn" --output tsv
$aciIp = az container show --name $AciName --resource-group $ResourceGroupName --query "ipAddress.ip" --output tsv

if ($aciFqdn) {
    $publicEndpoint = "http://${aciFqdn}:5000/convert"
    Write-Success "ACI Public Endpoint: $publicEndpoint"
} else {
    Write-Error "Failed to get ACI endpoint"
    exit 1
}

# Step 11: Wait for container to be ready and test
Write-Info "⏳ Waiting for container to start (this may take a few minutes)..."
Start-Sleep -Seconds 60

Write-Info "🧪 Testing container endpoint..."
$testUrl = "http://${aciFqdn}:5000"
try {
    $response = Invoke-WebRequest -Uri $testUrl -Method GET -TimeoutSec 30 -ErrorAction Stop
    Write-Success "Container is responding! Status: $($response.StatusCode)"
} catch {
    Write-Warning "Container may still be starting up. Check status with: az container show --name $AciName --resource-group $ResourceGroupName"
}

# Output summary
Write-Info ""
Write-Info "🎉 DEPLOYMENT SUMMARY"
Write-Info "===================="
Write-Success "Resource Group: $ResourceGroupName"
Write-Success "Azure Container Registry: $AcrName"
Write-Success "ACR Login Server: $acrLoginServer"
Write-Success "Container Image: $fullImageName"
Write-Success "Azure Container Instance: $AciName"
Write-Success "Container State: $aciState"
Write-Success "Public Endpoint: $publicEndpoint"
Write-Success "Public IP: $aciIp"

Write-Info ""
Write-Info "📝 NEXT STEPS:"
Write-Info "1. Update your Streamlit application to use: $publicEndpoint"
Write-Info "2. Test the endpoint with a simple HTTP request"
Write-Info "3. Monitor container logs with: az container logs --name $AciName --resource-group $ResourceGroupName"

# Create a config file for the Streamlit app
$configContent = @"
# Azure Container Instance Configuration
# Generated by deploy-to-azure.ps1 on $(Get-Date)

AZURE_CONVERTER_ENDPOINT = "$publicEndpoint"
AZURE_RESOURCE_GROUP = "$ResourceGroupName"
AZURE_ACI_NAME = "$AciName"
AZURE_ACR_NAME = "$AcrName"
"@

$configContent | Out-File -FilePath "azure-config.py" -Encoding UTF8
Write-Success "Configuration saved to azure-config.py"

Write-Info ""
Write-Info "✨ Deployment completed successfully!"
Write-Info "Your LibreOffice converter is now running in Azure!"
