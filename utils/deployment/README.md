# Deployment Utilities

This directory contains scripts for deploying the ExamSoft RTF Formatter to Azure.

## Scripts

### deploy-acr-build.sh
Builds Docker image and pushes to Azure Container Registry.

**Usage:**
```bash
./deploy-acr-build.sh
```

**What it does:**
- Builds Docker image from `../../streamlit-app/` directory
- Tags with incremented version number
- Pushes to Azure Container Registry
- Shows build status and image details

**Configuration:**
Edit the script to update:
- `ACR_NAME`: Your Azure Container Registry name
- `IMAGE_NAME`: Docker image name
- `SOURCE_DIR`: Source directory (default: ../../streamlit-app)

### update-aci.sh
Updates Azure Container Instance with new Docker image.

**Usage:**
```bash
./update-aci.sh
```

**What it does:**
- Deletes existing container instance
- Creates new instance with latest image version
- Maintains same DNS name and configuration
- Shows deployment status and public URL

**Configuration:**
Edit the script to update:
- `ACR_NAME`: Your Azure Container Registry name
- `RESOURCE_GROUP_NAME`: Azure resource group
- `ACI_NAME`: Container instance name
- `NEW_TAG`: Image version tag to deploy

## Prerequisites

- Azure CLI installed and logged in
- Docker installed (for local testing)
- Proper permissions to manage Azure resources
- Access to Azure Container Registry

## Quick Start

1. **First-time setup:**
   ```bash
   # Login to Azure
   az login
   
   # Set correct subscription
   az account set --subscription "your-subscription-id"
   
   # Login to container registry
   az acr login --name your-acr-name
   ```

2. **Deploy new version:**
   ```bash
   ./deploy-acr-build.sh  # Build and push
   ./update-aci.sh        # Update container
   ```

## Environment Variables

The deployment scripts use these Azure environment settings:

### Container Instance Configuration
- `STREAMLIT_SERVER_PORT=8501`
- `STREAMLIT_SERVER_ADDRESS=0.0.0.0`
- `STREAMLIT_SERVER_HEADLESS=true`

### Resource Allocation
- **CPU**: 1 core (adjustable in update-aci.sh)
- **Memory**: 2 GB (adjustable in update-aci.sh)
- **Port**: 8501

## Troubleshooting

### Common Issues

**Build failures:**
- Check Docker is running: `docker version`
- Verify source directory exists: `ls ../../streamlit-app/`
- Check Azure CLI login: `az account show`

**Deployment failures:**
- Verify container registry access: `az acr repository list --name your-acr-name`
- Check resource group exists: `az group show --name your-resource-group`
- Review container logs: `az container logs --name your-container --resource-group your-resource-group`

**Permission errors:**
- Ensure you have Container Registry and Container Instance permissions
- Check subscription limits: `az vm list-usage --location eastus`

### Useful Commands

```bash
# Check container status
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --query instanceView.state

# View container logs
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041

# List available image versions
az acr repository show-tags --name examsoftacr202508022041 --repository examsoft-rtf-formatter

# Test application health
curl -f http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501/_stcore/health
```

## Security Notes

- Scripts use admin credentials from Azure Container Registry
- Container instances have public IP addresses
- Consider using Azure Key Vault for sensitive configuration
- Regularly rotate ACR admin passwords

## Support

For deployment issues:
1. Check this README
2. Review Azure CLI documentation
3. Check container logs for application errors
4. Contact Charleston School of Law IT department