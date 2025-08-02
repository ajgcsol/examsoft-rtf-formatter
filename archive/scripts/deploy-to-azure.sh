#!/bin/bash

# Azure Container Deployment Script for ExamSoft LibreOffice Converter
# This script deploys the Docker container to Azure Container Registry and Azure Container Instance

# Default configuration
RESOURCE_GROUP_NAME=${1:-"examsoft-rg"}
LOCATION=${2:-"eastus"}
ACR_NAME=${3:-"examsoftacr$RANDOM"}
ACI_NAME=${4:-"examsoft-converter"}
IMAGE_NAME=${5:-"libreoffice-converter"}
IMAGE_TAG=${6:-"latest"}

# Color functions for output
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
warning() { echo -e "\033[33m⚠️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

info "🚀 Starting Azure Container Deployment for ExamSoft LibreOffice Converter"
info "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed"
    info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

success "Azure CLI detected: $(az version --query '"azure-cli"' -o tsv)"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
    info "Please install Docker and ensure it's running"
    exit 1
fi

if ! docker version &> /dev/null; then
    error "Docker is not running"
    info "Please start Docker and try again"
    exit 1
fi

success "Docker detected and running: $(docker version --format '{{.Server.Version}}')"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    error "Dockerfile not found in current directory"
    info "Please run this script from the exam-formatter directory"
    exit 1
fi

success "All prerequisites verified"

# Step 1: Login to Azure (if not already logged in)
info "🔐 Checking Azure authentication..."
if az account show &> /dev/null; then
    current_account=$(az account show --query "user.name" -o tsv)
    success "Already authenticated as: $current_account"
else
    info "Please authenticate with Azure..."
    az login
    if [ $? -ne 0 ]; then
        error "Azure authentication failed"
        exit 1
    fi
fi

# Step 2: Create Resource Group
info "📁 Creating resource group: $RESOURCE_GROUP_NAME"
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION" --output table
if [ $? -eq 0 ]; then
    success "Resource group created/verified: $RESOURCE_GROUP_NAME"
else
    error "Failed to create resource group"
    exit 1
fi

# Step 3: Create Azure Container Registry
info "🏗️  Creating Azure Container Registry: $ACR_NAME"
az acr create --resource-group "$RESOURCE_GROUP_NAME" --name "$ACR_NAME" --sku Basic --admin-enabled true --output table
if [ $? -eq 0 ]; then
    success "ACR created: $ACR_NAME"
else
    warning "ACR creation failed or already exists, continuing..."
fi

# Step 4: Get ACR login server
info "🔍 Getting ACR login server..."
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP_NAME" --query "loginServer" -o tsv)
if [ -n "$ACR_LOGIN_SERVER" ]; then
    success "ACR Login Server: $ACR_LOGIN_SERVER"
else
    error "Failed to get ACR login server"
    exit 1
fi

# Step 5: Login to ACR
info "🔐 Logging into Azure Container Registry..."
az acr login --name "$ACR_NAME"
if [ $? -eq 0 ]; then
    success "Successfully logged into ACR: $ACR_NAME"
else
    error "Failed to login to ACR"
    exit 1
fi

# Step 6: Build and tag Docker image
info "🔨 Building Docker image: $IMAGE_NAME"
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"
docker build -t "$FULL_IMAGE_NAME" .
if [ $? -eq 0 ]; then
    success "Docker image built: $FULL_IMAGE_NAME"
else
    error "Docker build failed"
    exit 1
fi

# Step 7: Push image to ACR
info "📤 Pushing image to Azure Container Registry..."
docker push "$FULL_IMAGE_NAME"
if [ $? -eq 0 ]; then
    success "Image pushed to ACR: $FULL_IMAGE_NAME"
else
    error "Failed to push image to ACR"
    exit 1
fi

# Step 8: Get ACR credentials for ACI
info "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
    success "ACR credentials retrieved"
else
    error "Failed to get ACR credentials"
    exit 1
fi

# Step 9: Create Azure Container Instance
info "🚀 Creating Azure Container Instance: $ACI_NAME"
az container create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$ACI_NAME" \
    --image "$FULL_IMAGE_NAME" \
    --registry-login-server "$ACR_LOGIN_SERVER" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --dns-name-label "$ACI_NAME" \
    --ports 5000 \
    --cpu 1 \
    --memory 2 \
    --restart-policy Always \
    --output table

if [ $? -eq 0 ]; then
    success "Azure Container Instance created: $ACI_NAME"
else
    error "Failed to create Azure Container Instance"
    exit 1
fi

# Step 10: Get ACI public endpoint
info "🌐 Getting ACI public endpoint..."
ACI_STATE=$(az container show --name "$ACI_NAME" --resource-group "$RESOURCE_GROUP_NAME" --query "instanceView.state" -o tsv)
ACI_FQDN=$(az container show --name "$ACI_NAME" --resource-group "$RESOURCE_GROUP_NAME" --query "ipAddress.fqdn" -o tsv)
ACI_IP=$(az container show --name "$ACI_NAME" --resource-group "$RESOURCE_GROUP_NAME" --query "ipAddress.ip" -o tsv)

if [ -n "$ACI_FQDN" ]; then
    PUBLIC_ENDPOINT="http://$ACI_FQDN:5000/convert"
    success "ACI Public Endpoint: $PUBLIC_ENDPOINT"
else
    error "Failed to get ACI endpoint"
    exit 1
fi

# Step 11: Wait for container to be ready and test
info "⏳ Waiting for container to start (this may take a few minutes)..."
sleep 60

info "🧪 Testing container endpoint..."
TEST_URL="http://$ACI_FQDN:5000"
if curl -f -s --connect-timeout 30 "$TEST_URL" > /dev/null; then
    success "Container is responding!"
else
    warning "Container may still be starting up. Check status with: az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME"
fi

# Output summary
echo ""
info "🎉 DEPLOYMENT SUMMARY"
info "===================="
success "Resource Group: $RESOURCE_GROUP_NAME"
success "Azure Container Registry: $ACR_NAME"
success "ACR Login Server: $ACR_LOGIN_SERVER"
success "Container Image: $FULL_IMAGE_NAME"
success "Azure Container Instance: $ACI_NAME"
success "Container State: $ACI_STATE"
success "Public Endpoint: $PUBLIC_ENDPOINT"
success "Public IP: $ACI_IP"

echo ""
info "📝 NEXT STEPS:"
info "1. Update your Streamlit application to use: $PUBLIC_ENDPOINT"
info "2. Test the endpoint with a simple HTTP request"
info "3. Monitor container logs with: az container logs --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME"

# Create a config file for the Streamlit app
cat > azure-config.py << EOF
# Azure Container Instance Configuration
# Generated by deploy-to-azure.sh on $(date)

AZURE_CONVERTER_ENDPOINT = "$PUBLIC_ENDPOINT"
AZURE_RESOURCE_GROUP = "$RESOURCE_GROUP_NAME"
AZURE_ACI_NAME = "$ACI_NAME"
AZURE_ACR_NAME = "$ACR_NAME"
EOF

success "Configuration saved to azure-config.py"

echo ""
info "✨ Deployment completed successfully!"
info "Your LibreOffice converter is now running in Azure!"
