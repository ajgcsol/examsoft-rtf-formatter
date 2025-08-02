#!/bin/bash

# Deploy the built image to Azure Container Instance

# Use the registry we just created
ACR_NAME="examsoftacr202508022041"
RESOURCE_GROUP_NAME="examsoft-rg-202508022041"
ACI_NAME="examsoft-streamlit-$(date +%s)"
IMAGE_NAME="examsoft-rtf-formatter"
TAG="latest"

# Color functions
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

info "🚀 Deploying to Azure Container Instance..."

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

FULL_IMAGE_NAME="$ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG"

info "Creating Azure Container Instance: $ACI_NAME"
info "Using image: $FULL_IMAGE_NAME"

# Create ACI
az container create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $ACI_NAME \
    --image $FULL_IMAGE_NAME \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $ACI_NAME \
    --ports 8501 \
    --cpu 1 \
    --memory 2 \
    --os-type Linux \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true

if [ $? -eq 0 ]; then
    success "ACI created successfully"
    
    # Get public URL
    ACI_FQDN=$(az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --query ipAddress.fqdn --output tsv)
    
    success "🎉 Deployment Complete!"
    success "📱 App URL: http://$ACI_FQDN:8501"
    
else
    error "Failed to create ACI"
    exit 1
fi