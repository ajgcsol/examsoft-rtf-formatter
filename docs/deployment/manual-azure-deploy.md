# Manual Azure Deployment Commands for ExamSoft Streamlit

## Prerequisites
You'll need to run these commands on a machine with Azure CLI installed and logged in.

## Step 1: Set Variables
```bash
RESOURCE_GROUP="CSOLIT"
ACR_NAME="examsoftacrprd"
IMAGE_NAME="examsoft-streamlit"
TAG="latest"
APP_NAME="examsoft-streamlit"
```

## Step 2: Build and Push to ACR
```bash
# Login to Azure (if not already)
az login

# Navigate to the project directory
cd /path/to/examsoft-rtf-formatter

# Build and push directly to ACR
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$TAG \
  --file streamlit-app/Dockerfile \
  streamlit-app/
```

## Step 3: Deploy to Azure Container Instance
```bash
# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Stop existing container if it exists
az container delete --name $APP_NAME --resource-group $RESOURCE_GROUP --yes || true

# Create new container instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label $APP_NAME \
  --ports 8501 \
  --cpu 1 \
  --memory 2 \
  --restart-policy Always
```

## Step 4: Get Application URL
```bash
# Get the URL
ACI_FQDN=$(az container show --name $APP_NAME --resource-group $RESOURCE_GROUP --query ipAddress.fqdn --output tsv)
echo "🌐 Your app is available at: http://$ACI_FQDN:8501"
```

## Step 5: Monitor Deployment
```bash
# Check deployment status
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" \
  --output table

# View logs
az container logs --name $APP_NAME --resource-group $RESOURCE_GROUP
```

## Expected Output
After successful deployment, you should see:
- Container Instance URL: `http://examsoft-streamlit.eastus.azurecontainer.io:8501`
- Healthy status check
- Streamlit app running and accessible

## Next Steps
1. Update Microsoft 365 app registration redirect URI to include the new container URL
2. Test all authentication and SharePoint functionality
3. Verify file upload and email notifications work correctly