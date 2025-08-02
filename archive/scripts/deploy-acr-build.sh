#!/bin/bash

# Azure ACR Build Deployment for ExamSoft Streamlit App
# This uses Azure Container Registry's cloud build capability

set -e

# Color functions
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

# Configuration
RESOURCE_GROUP="examsoft-rg"
ACR_NAME="examsoftacr"
APP_NAME="examsoft-streamlit-app"
IMAGE_NAME="examsoft-streamlit"

info "🚀 Azure ACR Build Deploy: ExamSoft Streamlit App"
info "=============================================="

# Check if we're logged in to Azure
if ! az account show &> /dev/null; then
    error "Please login to Azure first: az login"
    exit 1
fi

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

info "Using ACR: $ACR_LOGIN_SERVER"

# Build in Azure (cloud build)
FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:latest"

info "🔨 Building Docker image in Azure..."
az acr build --registry $ACR_NAME --image $IMAGE_NAME:latest ./streamlit-app

if [ $? -eq 0 ]; then
    success "Image built successfully in Azure"
else
    error "Failed to build image in Azure"
    exit 1
fi

# Stop existing container if it exists
if az container show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    info "🛑 Stopping existing container..."
    az container delete --name $APP_NAME --resource-group $RESOURCE_GROUP --yes
    sleep 15
fi

# Deploy new container
info "🚀 Deploying new container..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $FULL_IMAGE_NAME \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $APP_NAME \
    --ports 8501 \
    --os-type Linux \
    --cpu 1 \
    --memory 2 \
    --restart-policy Always

# Get the URL
sleep 10
ACI_FQDN=$(az container show --name $APP_NAME --resource-group $RESOURCE_GROUP --query ipAddress.fqdn --output tsv)

success "=============================================="
success "🎉 Deployment Complete!"
success "🌐 Your ExamSoft RTF Formatter is available at:"
success "   http://$ACI_FQDN:8501"
success "=============================================="
success ""
success "📋 Useful commands:"
success "View logs: az container logs --name $APP_NAME --resource-group $RESOURCE_GROUP"
success "Restart: az container restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
success ""
success "🔄 To redeploy after code changes:"
success "   Run this script again - it will rebuild and redeploy automatically"
