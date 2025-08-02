#!/bin/bash

# Azure Container Deployment Script for ExamSoft Streamlit App
# This script deploys the Streamlit Docker container to Azure Container Registry and Azure Container Instance

# Default configuration
RESOURCE_GROUP_NAME=${1:-"examsoft-rg"}
LOCATION=${2:-"eastus"}
ACR_NAME=${3:-"examsoftacr"}
ACI_NAME_STREAMLIT=${4:-"examsoft-streamlit-app"}
IMAGE_NAME_STREAMLIT=${5:-"examsoft-streamlit"}
IMAGE_TAG=${6:-"latest"}

# Color functions for output
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
warning() { echo -e "\033[33m⚠️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

info "🚀 Starting Azure Container Deployment for ExamSoft Streamlit App"
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

# Check if resource group exists
info "Checking for resource group: $RESOURCE_GROUP_NAME"
if az group show --name $RESOURCE_GROUP_NAME &> /dev/null; then
    success "Resource group $RESOURCE_GROUP_NAME already exists"
else
    info "Creating resource group: $RESOURCE_GROUP_NAME"
    az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
    if [ $? -eq 0 ]; then
        success "Resource group created successfully"
    else
        error "Failed to create resource group"
        exit 1
    fi
fi

# Check if ACR exists
info "Checking for Azure Container Registry: $ACR_NAME"
if az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME &> /dev/null; then
    success "ACR $ACR_NAME already exists"
else
    info "Creating Azure Container Registry: $ACR_NAME"
    az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic --admin-enabled true
    if [ $? -eq 0 ]; then
        success "ACR created successfully"
    else
        error "Failed to create ACR"
        exit 1
    fi
fi

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME --query loginServer --output tsv)
success "ACR login server: $ACR_LOGIN_SERVER"

# Build and push Streamlit Docker image
info "Building Streamlit Docker image..."
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME_STREAMLIT:$IMAGE_TAG"

# Build from the streamlit-app directory for cleaner image
docker build -t $FULL_IMAGE_NAME ./streamlit-app
if [ $? -eq 0 ]; then
    success "Streamlit Docker image built successfully"
else
    error "Failed to build Streamlit Docker image"
    exit 1
fi

info "Logging in to ACR..."
az acr login --name $ACR_NAME
if [ $? -eq 0 ]; then
    success "Logged in to ACR successfully"
else
    error "Failed to login to ACR"
    exit 1
fi

info "Pushing Streamlit image to ACR..."
docker push $FULL_IMAGE_NAME
if [ $? -eq 0 ]; then
    success "Streamlit image pushed to ACR successfully"
else
    error "Failed to push Streamlit image to ACR"
    exit 1
fi

# Get ACR credentials
info "Retrieving ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Check if Streamlit ACI already exists
info "Checking for existing Streamlit ACI: $ACI_NAME_STREAMLIT"
if az container show --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME &> /dev/null; then
    warning "ACI $ACI_NAME_STREAMLIT already exists. Deleting it..."
    az container delete --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME --yes
    if [ $? -eq 0 ]; then
        success "Existing ACI deleted successfully"
        info "Waiting for deletion to complete..."
        sleep 30
    else
        error "Failed to delete existing ACI"
        exit 1
    fi
fi

# Create Streamlit ACI
info "Creating Streamlit Azure Container Instance: $ACI_NAME_STREAMLIT"
az container create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $ACI_NAME_STREAMLIT \
    --image $FULL_IMAGE_NAME \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $ACI_NAME_STREAMLIT \
    --ports 8501 \
    --cpu 1 \
    --memory 2 \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_SERVER_ENABLE_CORS=false \
        STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

if [ $? -eq 0 ]; then
    success "Streamlit ACI created successfully"
    
    # Get the public IP and FQDN
    info "Getting Streamlit ACI details..."
    ACI_IP=$(az container show --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME --query ipAddress.ip --output tsv)
    ACI_FQDN=$(az container show --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME --query ipAddress.fqdn --output tsv)
    
    success "=================================================="
    success "🎉 Streamlit App Deployment Completed Successfully!"
    success "=================================================="
    success "📱 Streamlit App URL: http://$ACI_FQDN:8501"
    success "🌐 Public IP: $ACI_IP"
    success "📝 Container Name: $ACI_NAME_STREAMLIT"
    success "🏷️  Image: $FULL_IMAGE_NAME"
    success "=================================================="
    
    # Wait a moment for the container to start
    info "Waiting for container to start..."
    sleep 15
    
    # Check container status
    info "Checking container status..."
    CONTAINER_STATE=$(az container show --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME --query containers[0].instanceView.currentState.state --output tsv)
    
    if [ "$CONTAINER_STATE" = "Running" ]; then
        success "✅ Container is running!"
        success "🚀 Your ExamSoft RTF Formatter is now available at: http://$ACI_FQDN:8501"
        success ""
        success "🔍 To check logs:"
        success "   az container logs --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME"
        success ""
        success "🛠️  To update the app:"
        success "   1. Make your code changes"
        success "   2. Run this deployment script again"
        success "   3. The container will be recreated with the latest code"
        
    else
        warning "Container state: $CONTAINER_STATE"
        warning "The container may still be starting. Check the logs with:"
        warning "az container logs --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME"
    fi
else
    error "Failed to create Streamlit ACI"
    exit 1
fi

info ""
info "🎯 Deployment Summary:"
info "- Resource Group: $RESOURCE_GROUP_NAME"
info "- Azure Container Registry: $ACR_NAME"
info "- Streamlit Container: $ACI_NAME_STREAMLIT"
info "- Streamlit App URL: http://$ACI_FQDN:8501"
info ""
info "📋 Useful Commands:"
info "View logs: az container logs --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME"
info "Restart container: az container restart --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME"
info "Delete container: az container delete --name $ACI_NAME_STREAMLIT --resource-group $RESOURCE_GROUP_NAME --yes"
