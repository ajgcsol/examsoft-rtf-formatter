# Azure CLI Setup and Deployment Guide

## Step 1: Install and Configure Azure CLI

### Option A: Download and Install
1. Download Azure CLI from: https://aka.ms/installazurecliwindows
2. Run the installer and follow the prompts
3. Restart your command prompt/PowerShell

### Option B: Manual PATH Configuration
If Azure CLI is installed but not in PATH:

1. Open PowerShell as Administrator
2. Run these commands one by one:

```powershell
# Check common installation locations
$locations = @(
    "${env:ProgramFiles}\Microsoft SDKs\Azure\CLI2\wbin",
    "${env:ProgramFiles(x86)}\Microsoft SDKs\Azure\CLI2\wbin", 
    "${env:LocalAppData}\Programs\Azure CLI\wbin"
)

foreach ($loc in $locations) {
    if (Test-Path "$loc\az.cmd") {
        Write-Host "Found Azure CLI at: $loc"
        # Add to system PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($currentPath -notlike "*$loc*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$loc", "Machine")
            Write-Host "Added to system PATH"
        }
        # Add to current session
        $env:PATH = "$env:PATH;$loc"
        break
    }
}
```

3. Test Azure CLI: `az --version`

## Step 2: Login to Azure

```powershell
az login
```

This will open a browser window for authentication.

## Step 3: Set Your Subscription (if you have multiple)

```powershell
# List available subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "Your-Subscription-Name-Or-ID"
```

## Step 4: Deploy to Azure

Run the deployment script with execution policy bypass:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1
```

### Optional Parameters:
```powershell
# Custom resource group and location
PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1 -ResourceGroupName "MyResourceGroup" -Location "eastus2"

# Custom ACR name (must be globally unique)
PowerShell -ExecutionPolicy Bypass -File .\deploy-to-azure.ps1 -AcrName "myuniqueacr12345"
```

## What the Deployment Script Does:

1. **Checks Prerequisites**: Verifies Azure CLI and Docker are installed
2. **Creates Resource Group**: Creates or uses existing resource group
3. **Creates Azure Container Registry (ACR)**: For storing the Docker image
4. **Builds Docker Image**: Builds the LibreOffice converter image locally
5. **Pushes to ACR**: Uploads the image to Azure Container Registry
6. **Creates Container Instance**: Deploys the container to Azure Container Instances
7. **Configures Public Access**: Sets up public endpoint for the API
8. **Saves Configuration**: Creates azure_config.json for the Streamlit app

## Expected Resources Created:

- **Resource Group**: Container for all resources
- **Azure Container Registry**: For Docker image storage
- **Azure Container Instance**: Running container with public IP
- **Public IP**: Accessible endpoint for the LibreOffice API

## After Deployment:

1. The script will output the public IP address of your container
2. Test the endpoint: `http://YOUR-PUBLIC-IP:5000/health`
3. The Streamlit app will automatically detect and use the Azure endpoint
4. Configuration is saved in `azure_config.json`

## Troubleshooting:

### If Azure CLI is not found:
- Make sure it's installed from https://aka.ms/installazurecliwindows
- Restart your terminal after installation
- Check PATH environment variable

### If deployment fails:
- Check you're logged into Azure: `az account show`
- Verify you have permissions to create resources
- Check the resource group name doesn't conflict
- Ensure ACR name is globally unique (lowercase, alphanumeric)

### If container doesn't start:
- Check container logs: `az container logs --resource-group RESOURCEGROUP --name examsoft-converter`
- Verify Docker image built correctly
- Check container status: `az container show --resource-group RESOURCEGROUP --name examsoft-converter`

## Cost Information:

- **Azure Container Registry**: Basic tier ~$5/month
- **Azure Container Instances**: ~$0.0012/vCPU-second + $0.000125/GB-second
- **Estimated monthly cost**: $10-20 for light usage

## Cleanup (when no longer needed):

```powershell
az group delete --name CSOLIT --yes --no-wait
```

This will delete all resources in the resource group.
