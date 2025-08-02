# Deployment Guide

## Overview

This guide covers deploying the ExamSoft RTF Formatter to Azure Container Instances using Azure Container Registry.

## Prerequisites

### Required Tools
- Azure CLI (latest version)
- Docker (for local testing)
- Git
- Bash shell (Windows: Git Bash or WSL)

### Azure Resources
- Azure subscription with Container Registry and Container Instances enabled
- Resource group for the application
- Azure Container Registry
- Appropriate permissions to create and manage resources

## Quick Deployment

### Current Production Setup
- **Registry**: `examsoftacr202508022041.azurecr.io`
- **Resource Group**: `examsoft-rg-202508022041`
- **Container Instance**: `examsoft-streamlit-1754167662`

### Deploy New Version
```bash
# Navigate to deployment scripts
cd utils/deployment

# Build and push new image to ACR
./deploy-acr-build.sh

# Update running container with new image
./update-aci.sh
```

## Detailed Deployment Process

### 1. Initial Azure Setup

#### Create Resource Group
```bash
az group create --name examsoft-rg-$(date +%Y%m%d%H%M) --location eastus
```

#### Create Container Registry
```bash
ACR_NAME="examsoftacr$(date +%Y%m%d%H%M)"
az acr create --resource-group examsoft-rg-$(date +%Y%m%d%H%M) --name $ACR_NAME --sku Basic --admin-enabled true
```

### 2. Configure Deployment Scripts

#### Update deploy-acr-build.sh
```bash
# Edit deployment script
vim utils/deployment/deploy-acr-build.sh

# Update these variables:
ACR_NAME="your-acr-name"
IMAGE_NAME="examsoft-rtf-formatter"
SOURCE_DIR="./streamlit-app"
```

#### Update update-aci.sh
```bash
# Edit container update script
vim utils/deployment/update-aci.sh

# Update these variables:
ACR_NAME="your-acr-name"
RESOURCE_GROUP_NAME="your-resource-group"
ACI_NAME="your-container-instance-name"
```

### 3. Build and Deploy

#### Initial Deployment
```bash
# Build and push image
cd utils/deployment
./deploy-acr-build.sh

# Create container instance
az container create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $ACI_NAME \
    --image $ACR_LOGIN_SERVER/examsoft-rtf-formatter:v1 \
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
```

#### Subsequent Deployments
```bash
# Build new version
./deploy-acr-build.sh

# Update running container
./update-aci.sh
```

### 4. Verify Deployment

#### Check Container Status
```bash
az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --query instanceView.state
```

#### Test Application
```bash
# Get public URL
ACI_FQDN=$(az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --query ipAddress.fqdn --output tsv)
echo "Application URL: http://$ACI_FQDN:8501"

# Health check
curl -f http://$ACI_FQDN:8501/_stcore/health
```

## Configuration

### Environment Variables

The container is configured with these environment variables:
- `STREAMLIT_SERVER_PORT=8501`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`

### Resource Allocation

Current settings:
- **CPU**: 1 core
- **Memory**: 2 GB
- **Port**: 8501

To modify resources, edit `update-aci.sh`:
```bash
--cpu 2 \
--memory 4 \
```

### Azure App Registration

For Microsoft 365 integration, configure in `streamlit-app/azure_config.json`:
```json
{
  "client_id": "your-app-registration-client-id",
  "tenant_id": "your-tenant-id",
  "authority": "https://login.microsoftonline.com/your-tenant-id",
  "redirect_uri": "http://your-app-url:8501/auth/callback"
}
```

## Deployment Scripts Reference

### deploy-acr-build.sh
- Builds Docker image from `streamlit-app/` directory
- Pushes to Azure Container Registry
- Automatically increments version tag
- Displays build status and image details

### update-aci.sh
- Deletes existing container instance
- Creates new instance with latest image
- Maintains same configuration and DNS name
- Shows deployment status and URL

## Troubleshooting Deployment

### Common Issues

#### 1. Azure CLI Authentication
```bash
# Login to Azure
az login

# Set correct subscription
az account set --subscription "your-subscription-id"

# Verify login
az account show
```

#### 2. Container Registry Access
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Test ACR connectivity
az acr repository list --name $ACR_NAME
```

#### 3. Image Build Failures
```bash
# Check Docker is running
docker version

# Test local build
cd streamlit-app
docker build -t test-image .

# Check for syntax errors in Dockerfile
docker build --no-cache -t test-image .
```

#### 4. Container Instance Issues
```bash
# Check container logs
az container logs --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME

# View container events
az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --query instanceView.events
```

### Error Messages

#### "Unable to pull image"
- Check ACR credentials are correct
- Verify image exists: `az acr repository show-tags --name $ACR_NAME --repository examsoft-rtf-formatter`
- Ensure network connectivity to ACR

#### "Port 8501 already in use"
- Delete existing container: `az container delete --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME --yes`
- Choose different port or DNS name

#### "Resource quota exceeded"
- Check Azure subscription limits
- Choose different region: `az account list-locations`
- Reduce resource allocation (CPU/memory)

## Security Considerations

### Network Security
- Container instances have public IP by default
- Consider using Azure Virtual Networks for private deployment
- Implement Azure Front Door for SSL termination

### Authentication
- Use managed identities where possible
- Store secrets in Azure Key Vault
- Regularly rotate credentials

### Image Security
- Scan images for vulnerabilities: `az acr check-health --name $ACR_NAME`
- Use minimal base images
- Keep dependencies updated

## Advanced Deployment Options

### Blue-Green Deployment
```bash
# Create staging environment
az container create --name $ACI_NAME-staging ...

# Test staging
curl -f http://$ACI_NAME-staging.eastus.azurecontainer.io:8501/_stcore/health

# Swap DNS or update load balancer
# Delete old production instance
```

### Multi-Region Deployment
```bash
# Deploy to multiple regions
for region in eastus westus2 centralus; do
    az container create \
        --name $ACI_NAME-$region \
        --location $region \
        ...
done
```

### Custom Domain Setup
```bash
# Create Azure Front Door
az afd profile create --profile-name examsoft-afd --resource-group $RESOURCE_GROUP_NAME

# Add custom domain
az afd custom-domain create \
    --custom-domain-name examsoft \
    --host-name examsoft.charlestonlaw.edu \
    --profile-name examsoft-afd \
    --resource-group $RESOURCE_GROUP_NAME
```

## Monitoring Setup

### Health Checks
```bash
# Built-in Streamlit health endpoint
curl http://$ACI_FQDN:8501/_stcore/health

# Custom health check script
#!/bin/bash
if curl -f -s http://$ACI_FQDN:8501/_stcore/health > /dev/null; then
    echo "Application healthy"
    exit 0
else
    echo "Application unhealthy"
    exit 1
fi
```

### Azure Monitor Integration
```bash
# Enable container insights
az monitor diagnostic-settings create \
    --name examsoft-diagnostics \
    --resource $CONTAINER_RESOURCE_ID \
    --logs '[{"category":"ContainerInstanceLog","enabled":true}]' \
    --workspace $LOG_ANALYTICS_WORKSPACE_ID
```

## Backup and Recovery

### Configuration Backup
```bash
# Export resource group template
az group export --name $RESOURCE_GROUP_NAME > backup-template.json

# Backup ACR images
az acr import --name backup-acr --source $ACR_NAME.azurecr.io/examsoft-rtf-formatter:latest
```

### Disaster Recovery
```bash
# Quick recovery script
#!/bin/bash
# Recreate from backup template
az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file backup-template.json

# Redeploy application
cd utils/deployment
./deploy-acr-build.sh
./update-aci.sh
```

## Cost Optimization

### Resource Sizing
- Monitor CPU/memory usage with Azure Monitor
- Adjust container resources based on actual usage
- Consider Azure Container Apps for automatic scaling

### Image Optimization
- Use multi-stage Docker builds
- Minimize image layers
- Use .dockerignore to exclude unnecessary files

### Scheduled Scaling
```bash
# Stop container during off-hours
az container stop --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME

# Start container during business hours
az container start --name $ACI_NAME --resource-group $RESOURCE_GROUP_NAME
```