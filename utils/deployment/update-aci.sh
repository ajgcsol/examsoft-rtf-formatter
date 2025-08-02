#!/bin/bash

# Update the container instance with the new version

ACR_NAME="examsoftacr202508022041"
RESOURCE_GROUP_NAME="examsoft-rg-202508022041"
ACI_NAME="examsoft-streamlit-1754167662"
IMAGE_NAME="examsoft-rtf-formatter"
NEW_TAG="v12"

# Color functions
success() { echo -e "\033[32m✅ $1\033[0m"; }
info() { echo -e "\033[36mℹ️  $1\033[0m"; }
error() { echo -e "\033[31m❌ $1\033[0m"; }

info "🔄 Updating container instance with new version..."

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

NEW_IMAGE="$ACR_LOGIN_SERVER/$IMAGE_NAME:$NEW_TAG"

info "Deleting existing container..."
az container delete --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --yes

info "Creating new container with updated image: $NEW_IMAGE"
az container create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $ACI_NAME \
    --image $NEW_IMAGE \
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
    success "Container updated successfully!"
    
    # Get public URL
    ACI_FQDN=$(az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --query ipAddress.fqdn --output tsv)
    
    success "🎉 Updated App URL: http://$ACI_FQDN:8501"
    success "🔥 Now running with all your latest changes including multiple tabs!"
    
else
    error "Failed to update container"
    exit 1
fi