# Azure Configuration Guide

## Overview

This guide covers setting up Azure resources and Microsoft 365 integration for the ExamSoft RTF Formatter.

## Azure Resource Setup

### 1. Subscription and Resource Group

#### Create Resource Group
```bash
# Set variables
RESOURCE_GROUP="examsoft-rg-$(date +%Y%m%d%H%M)"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

#### Verify Subscription Limits
```bash
# Check container instance quota
az vm list-usage --location $LOCATION --query "[?localName=='Container Groups'].{Name:localName,Current:currentValue,Limit:limit}"

# Check container registry quota
az provider show --namespace Microsoft.ContainerRegistry --query "resourceTypes[?resourceType=='registries'].locations[]"
```

### 2. Azure Container Registry (ACR)

#### Create ACR
```bash
ACR_NAME="examsoftacr$(date +%Y%m%d%H%M)"

az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --location $LOCATION
```

#### Configure ACR
```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Test ACR login
az acr login --name $ACR_NAME
```

### 3. Container Instance Configuration

#### Resource Specifications
- **CPU**: 1-2 cores (adjustable based on load)
- **Memory**: 2-4 GB (adjustable based on usage)
- **Storage**: Ephemeral (no persistent storage needed)
- **Networking**: Public IP with DNS label

#### Create Container Instance
```bash
ACI_NAME="examsoft-streamlit-$(date +%s)"

az container create \
    --resource-group $RESOURCE_GROUP \
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
    --restart-policy Always \
    --environment-variables \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_SERVER_ENABLE_CORS=false \
        STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
```

## Microsoft 365 Integration

### 1. Azure Active Directory App Registration

#### Create App Registration
```bash
# Create app registration
APP_NAME="ExamSoft RTF Formatter"
az ad app create --display-name "$APP_NAME"

# Get application ID
APP_ID=$(az ad app list --display-name "$APP_NAME" --query [0].appId --output tsv)
echo "Application ID: $APP_ID"
```

#### Configure Redirect URIs
```bash
# Get container public URL
ACI_FQDN=$(az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP --query ipAddress.fqdn --output tsv)
REDIRECT_URI="http://$ACI_FQDN:8501"

# Update app registration with redirect URI
az ad app update --id $APP_ID --web-redirect-uris "$REDIRECT_URI"
```

#### Create Client Secret
```bash
# Create client secret (valid for 2 years)
CLIENT_SECRET=$(az ad app credential reset --id $APP_ID --years 2 --query password --output tsv)
echo "Client Secret: $CLIENT_SECRET"

# Get tenant ID
TENANT_ID=$(az account show --query tenantId --output tsv)
echo "Tenant ID: $TENANT_ID"
```

### 2. API Permissions Configuration

#### Required Microsoft Graph Permissions
- `Sites.ReadWrite.All` - SharePoint site access
- `Files.ReadWrite.All` - File upload/download
- `Mail.Send` - Email notifications (optional)
- `User.Read` - Basic user profile

#### Add API Permissions
```bash
# Add Microsoft Graph permissions
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions 75359482-378d-4052-8f01-80520e7db3cd=Role  # Sites.ReadWrite.All
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions 75359482-378d-4052-8f01-80520e7db3cd=Role  # Files.ReadWrite.All
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions b633e1c5-b582-4048-a93e-9f11b44c7e96=Role  # Mail.Send
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope  # User.Read

# Grant admin consent (requires admin privileges)
az ad app permission admin-consent --id $APP_ID
```

#### Alternative: Manual Permission Setup
1. Navigate to Azure Portal → Azure Active Directory → App registrations
2. Find your app registration
3. Go to API permissions → Add a permission → Microsoft Graph
4. Add the required permissions listed above
5. Click "Grant admin consent"

### 3. SharePoint Site Configuration

#### Verify SharePoint Site Access
```bash
# Test SharePoint site exists
SITE_URL="https://charlestonlaw.sharepoint.com/sites/IT"

# Use PowerShell or Graph API to verify
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/charlestonlaw.sharepoint.com:/sites/IT"
```

#### Create Required Folders
The application expects this folder structure:
```
SharePoint Site: https://charlestonlaw.sharepoint.com/sites/IT
└── ExamSoft/
    └── File-converter/
        └── Import/
```

#### Folder Creation Script
```powershell
# PowerShell script to create folders
Connect-PnPOnline -Url "https://charlestonlaw.sharepoint.com/sites/IT" -Interactive

# Create folder structure
New-PnPFolder -Name "ExamSoft" -Folder "" -ErrorAction SilentlyContinue
New-PnPFolder -Name "File-converter" -Folder "ExamSoft" -ErrorAction SilentlyContinue
New-PnPFolder -Name "Import" -Folder "ExamSoft/File-converter" -ErrorAction SilentlyContinue
```

### 4. Application Configuration

#### Create Azure Configuration File
```bash
# Create azure_config.json for the application
cat > streamlit-app/azure_config.json << EOF
{
    "client_id": "$APP_ID",
    "tenant_id": "$TENANT_ID",
    "authority": "https://login.microsoftonline.com/$TENANT_ID",
    "redirect_uri": "http://$ACI_FQDN:8501"
}
EOF
```

#### Update Streamlit Secrets
```toml
# Create .streamlit/secrets.toml
[azure]
client_id = "$APP_ID"
tenant_id = "$TENANT_ID"
client_secret = "$CLIENT_SECRET"

[sharepoint]
site_url = "https://charlestonlaw.sharepoint.com/sites/IT"
folder_path = "ExamSoft/File-converter/Import"
```

## Security Configuration

### 1. Network Security

#### Public Access Configuration
```bash
# Current setup uses public IP
# For enhanced security, consider:

# 1. Virtual Network integration
az network vnet create --name examsoft-vnet --resource-group $RESOURCE_GROUP

# 2. Private endpoints
az network private-endpoint create \
    --name examsoft-pe \
    --resource-group $RESOURCE_GROUP \
    --vnet-name examsoft-vnet \
    --subnet default
```

### 2. SSL/TLS Configuration

#### Azure Front Door Setup (Optional)
```bash
# Create Front Door for SSL termination
az afd profile create \
    --profile-name examsoft-afd \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_AzureFrontDoor

# Add custom domain and SSL certificate
az afd custom-domain create \
    --custom-domain-name examsoft \
    --host-name examsoft.charlestonlaw.edu \
    --profile-name examsoft-afd \
    --resource-group $RESOURCE_GROUP
```

### 3. Identity and Access Management

#### Service Principal (Alternative to User Authentication)
```bash
# Create service principal for application
SP_NAME="examsoft-app-sp"
az ad sp create-for-rbac --name $SP_NAME --role Contributor --scopes /subscriptions/$(az account show --query id -o tsv)

# Assign SharePoint permissions
az ad app permission add --id $SP_APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions 75359482-378d-4052-8f01-80520e7db3cd=Role
```

## Monitoring and Logging

### 1. Azure Monitor Integration

#### Log Analytics Workspace
```bash
# Create Log Analytics workspace
WORKSPACE_NAME="examsoft-logs"
az monitor log-analytics workspace create \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --workspace-name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --query customerId --output tsv)
```

#### Container Insights
```bash
# Enable container insights
az container create \
    --name $ACI_NAME \
    --resource-group $RESOURCE_GROUP \
    --log-analytics-workspace $WORKSPACE_ID \
    --log-analytics-workspace-key $(az monitor log-analytics workspace get-shared-keys \
        --workspace-name $WORKSPACE_NAME \
        --resource-group $RESOURCE_GROUP \
        --query primarySharedKey --output tsv)
```

### 2. Application Insights (Optional)

#### Create Application Insights
```bash
# Create Application Insights instance
az monitor app-insights component create \
    --app examsoft-ai \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --workspace $WORKSPACE_ID

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app examsoft-ai \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey --output tsv)
```

## Backup and Disaster Recovery

### 1. Resource Templates

#### Export Configuration
```bash
# Export resource group template
az group export --name $RESOURCE_GROUP > examsoft-template.json

# Create parameter file
cat > examsoft-parameters.json << EOF
{
    "\$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "acrName": { "value": "$ACR_NAME" },
        "aciName": { "value": "$ACI_NAME" },
        "location": { "value": "$LOCATION" }
    }
}
EOF
```

### 2. Cross-Region Replication

#### Setup Secondary Region
```bash
# Replicate ACR to secondary region
SECONDARY_LOCATION="westus2"
az acr replication create \
    --registry $ACR_NAME \
    --location $SECONDARY_LOCATION
```

## Cost Optimization

### 1. Resource Scheduling

#### Auto-shutdown Script
```bash
#!/bin/bash
# Stop container during off-hours (example: 10 PM - 6 AM EST)
if [ $(date +%H) -ge 22 ] || [ $(date +%H) -lt 6 ]; then
    az container stop --name $ACI_NAME --resource-group $RESOURCE_GROUP
else
    az container start --name $ACI_NAME --resource-group $RESOURCE_GROUP
fi
```

### 2. Resource Sizing

#### Monitor and Adjust
```bash
# Check resource utilization
az monitor metrics list \
    --resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/$ACI_NAME" \
    --metric "CpuUsage,MemoryUsage"

# Adjust based on usage patterns
# Update update-aci.sh with appropriate --cpu and --memory values
```

## Troubleshooting

### Common Azure Issues

#### Authentication Failures
```bash
# Check app registration
az ad app show --id $APP_ID --query "{displayName:displayName,appId:appId,signInAudience:signInAudience}"

# Verify permissions
az ad app permission list --id $APP_ID
```

#### Container Instance Issues
```bash
# Check container status
az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP --query instanceView

# View container logs
az container logs --name $ACI_NAME --resource-group $RESOURCE_GROUP

# Check container events
az container show --name $ACI_NAME --resource-group $RESOURCE_GROUP --query instanceView.events
```

#### SharePoint Access Issues
```bash
# Test Graph API access
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/charlestonlaw.sharepoint.com"

# Verify folder structure
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/$SITE_ID/drive/root:/Shared%20Documents/ExamSoft"
```

### Support Resources

- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Microsoft Graph API**: https://docs.microsoft.com/graph/
- **Azure Support**: Create ticket in Azure Portal
- **Community Support**: https://stackoverflow.com/questions/tagged/azure