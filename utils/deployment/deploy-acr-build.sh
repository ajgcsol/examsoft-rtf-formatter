#!/bin/bash

# Azure Container Registry Build Script for ExamSoft RTF Formatter
# This script builds the Docker image directly in Azure Container Registry

# Generate unique registry name with timestamp
TIMESTAMP=$(date +%Y%m%d%H%M)
ACR_NAME="examsoftacr${TIMESTAMP}"
RESOURCE_GROUP_NAME="examsoft-rg-${TIMESTAMP}"
LOCATION="eastus"
IMAGE_NAME="examsoft-rtf-formatter"
TAG="latest"

# Color functions for output
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
warning() { echo -e "\033[33m⚠️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

info "🚀 Starting Azure Container Registry Build"
info "Registry Name: $ACR_NAME"
info "Resource Group: $RESOURCE_GROUP_NAME"
info "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed"
    info "Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

success "Azure CLI detected: $(az version --query '"azure-cli"' -o tsv)"

# Login check
info "Checking Azure login status..."
if ! az account show &> /dev/null; then
    warning "Not logged in to Azure"
    info "Please login to Azure..."
    az login
    if [ $? -ne 0 ]; then
        error "Azure login failed"
        exit 1
    fi
fi

CURRENT_SUBSCRIPTION=$(az account show --query name -o tsv)
success "Logged in to Azure subscription: $CURRENT_SUBSCRIPTION"

# Create resource group
info "Creating resource group: $RESOURCE_GROUP_NAME"
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
if [ $? -eq 0 ]; then
    success "Resource group created successfully"
else
    error "Failed to create resource group"
    exit 1
fi

# Create Azure Container Registry
info "Creating Azure Container Registry: $ACR_NAME"
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic --admin-enabled true
if [ $? -eq 0 ]; then
    success "ACR created successfully"
else
    error "Failed to create ACR"
    exit 1
fi

# Build image directly in ACR
info "Building Docker image in Azure Container Registry..."
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$TAG \
  --file streamlit-app/Dockerfile \
  streamlit-app/

if [ $? -eq 0 ]; then
    success "Docker image built successfully in ACR"
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME --query loginServer --output tsv)
    
    success "=================================================="
    success "🎉 Build Completed Successfully!"
    success "=================================================="
    success "🏷️  Registry: $ACR_NAME"
    success "🌐 Login Server: $ACR_LOGIN_SERVER"
    success "📷 Image: $IMAGE_NAME:$TAG"
    success "🔗 Full Image Name: $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG"
    success "=================================================="
    
    info "📋 Useful Commands:"
    info "View repositories: az acr repository list --name $ACR_NAME --output table"
    info "View image tags: az acr repository show-tags --name $ACR_NAME --repository $IMAGE_NAME --output table"
    info "Delete registry: az acr delete --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME --yes"
    
else
    error "Failed to build Docker image in ACR"
    exit 1
fi