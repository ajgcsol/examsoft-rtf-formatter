# Azure Deployment Guide for ExamSoft LibreOffice Converter

This guide explains how to deploy the LibreOffice Docker container to Azure Container Registry (ACR) and Azure Container Instance (ACI) for cloud-based document conversion.

## 🚀 Quick Start

### **Step 1: Install Azure CLI (if not already installed)**

#### Option A: Automatic Installation (Recommended)
```powershell
# PowerShell (run as Administrator)
.\install-azure-cli.ps1
```

#### Option B: Simple Batch Script
```cmd
# Command Prompt
.\install-azure-cli.bat
```

#### Option C: Manual Installation
- Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
- Or use winget: `winget install Microsoft.AzureCLI`

### **Step 2: Authenticate with Azure**
```bash
az login
az account show  # Verify authentication
```

### **Step 3: Deploy to Azure**

#### Option 1: PowerShell (Windows)
```powershell
.\deploy-to-azure.ps1
```

#### Option 2: Bash (Linux/macOS/WSL)
```bash
./deploy-to-azure.sh
```

## 📋 Prerequisites

Before running the deployment script, ensure you have:

1. **Azure CLI** installed and configured
   - **Quick Install**: Run `.\install-azure-cli.ps1` or `.\install-azure-cli.bat`
   - **Manual Install**: See [AZURE_CLI_INSTALL.md](AZURE_CLI_INSTALL.md) for detailed instructions
   - **Download**: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   - **Login**: `az login`

2. **Docker** installed and running
   - Download: https://www.docker.com/products/docker-desktop

3. **Active Azure Subscription**
   - Verify: `az account show`

## 🔧 Script Parameters

Both scripts accept optional parameters:

### PowerShell Script
```powershell
.\deploy-to-azure.ps1 -ResourceGroupName "my-rg" -Location "westus2" -AcrName "myacr123" -AciName "my-converter"
```

### Bash Script
```bash
./deploy-to-azure.sh "my-rg" "westus2" "myacr123" "my-converter"
```

### Parameter Details
- **ResourceGroupName/Arg1**: Azure resource group name (default: `examsoft-rg`)
- **Location/Arg2**: Azure region (default: `eastus`)
- **AcrName/Arg3**: Container registry name (default: auto-generated)
- **AciName/Arg4**: Container instance name (default: `examsoft-converter`)

## 📁 What the Script Creates

1. **Azure Resource Group**: Contains all resources
2. **Azure Container Registry (ACR)**: Stores your Docker image
3. **Azure Container Instance (ACI)**: Runs your converter service
4. **Public Endpoint**: HTTP endpoint for the conversion API
5. **Configuration File**: `azure-config.py` for Streamlit integration

## 🌐 After Deployment

### Automatic Configuration
The deployment script automatically creates `azure-config.py` with your endpoint details:

```python
AZURE_CONVERTER_ENDPOINT = "http://your-container.eastus.azurecontainer.io:5000/convert"
AZURE_RESOURCE_GROUP = "examsoft-rg"
AZURE_ACI_NAME = "examsoft-converter"
AZURE_ACR_NAME = "examsoftacr1234"
```

### Streamlit Integration
Your Streamlit app will automatically detect and use the Azure endpoint. You'll see:

- 🌤️ **Using Azure Cloud Endpoint** (instead of local Docker)
- Azure configuration details in the expandable section
- Test button to verify the endpoint is working

## 🔍 Monitoring & Management

### Check Deployment Status
```bash
az container show --name examsoft-converter --resource-group examsoft-rg
```

### View Container Logs
```bash
az container logs --name examsoft-converter --resource-group examsoft-rg
```

### Restart Container
```bash
az container restart --name examsoft-converter --resource-group examsoft-rg
```

### Test Endpoint Manually
```bash
curl http://your-container.eastus.azurecontainer.io:5000
```

## 💰 Cost Considerations

**Azure Container Instance Pricing (as of 2024):**
- **CPU**: ~$0.0000125 per vCPU-second
- **Memory**: ~$0.0000014 per GB-second
- **Example**: 1 vCPU + 2GB RAM running 24/7 ≈ $35-40/month

**Cost Optimization Tips:**
- Use the ACI for on-demand conversion rather than 24/7 operation
- Consider Azure Container Apps for auto-scaling if usage varies
- Monitor usage with Azure Cost Management

## 🛠️ Troubleshooting

### Common Issues

**1. Docker Build Fails**
```bash
# Check if Dockerfile exists
ls -la Dockerfile

# Verify Docker is running
docker version
```

**2. Azure CLI Not Authenticated**
```bash
az login
az account show
```

**3. Container Won't Start**
```bash
# Check container logs
az container logs --name examsoft-converter --resource-group examsoft-rg

# Check container status
az container show --name examsoft-converter --resource-group examsoft-rg --query "instanceView"
```

**4. Endpoint Not Responding**
- Wait 2-3 minutes after deployment for container to fully start
- Check if the container is in "Running" state
- Verify firewall/network settings allow HTTP traffic on port 5000

### Getting Help

**View Container Details:**
```bash
az container show --name examsoft-converter --resource-group examsoft-rg --output table
```

**Container Resource Usage:**
```bash
az container show --name examsoft-converter --resource-group examsoft-rg --query "containers[0].resources"
```

## 🔄 Updates & Redeployment

To update your deployment with code changes:

1. **Rebuild and redeploy:**
   ```bash
   ./deploy-to-azure.sh
   ```

2. **Or update just the container:**
   ```bash
   # Build new image
   docker build -t your-acr.azurecr.io/libreoffice-converter:latest .
   
   # Push to ACR
   az acr login --name your-acr
   docker push your-acr.azurecr.io/libreoffice-converter:latest
   
   # Restart container to pull new image
   az container restart --name examsoft-converter --resource-group examsoft-rg
   ```

## 🗑️ Cleanup

To remove all Azure resources:

```bash
# Delete the entire resource group (removes everything)
az group delete --name examsoft-rg --yes --no-wait

# Or delete individual resources
az container delete --name examsoft-converter --resource-group examsoft-rg --yes
az acr delete --name your-acr --resource-group examsoft-rg --yes
```

## 🔐 Security Considerations

1. **Network Security**: The container instance has a public IP by default
2. **Access Control**: Consider using Azure Private Endpoints for production
3. **Authentication**: The current setup doesn't include authentication
4. **Resource Limits**: CPU and memory are limited to prevent abuse

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Azure CLI and Docker documentation
3. Verify your Azure subscription has sufficient permissions
4. Check Azure service health for any regional issues

---

**Happy deploying! 🚀**
