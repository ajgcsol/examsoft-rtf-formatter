# ExamSoft RTF Formatter v2.0 - Complete Deployment Guide

## 🚀 New Features in v2.0

- ✅ **Dual input methods**: Text paste vs File upload tabs
- ✅ **Multi-format support**: docx, rtf, txt, csv, xlsx files
- ✅ **Auto instruction parsing**: Separates instructions from questions automatically
- ✅ **Dynamic SharePoint sites**: Loads all accessible sites via Graph API
- ✅ **Advanced folder browser**: Tree navigation with favorites and breadcrumbs
- ✅ **Email notifications**: Sends notifications after file upload
- ✅ **Better error handling**: Clear user feedback and permission checking

## 🐳 Docker Containerization

### 1. Create Production Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY streamlit_app_fixed.py streamlit_app.py
COPY safe_formatter.py .
COPY examsoft_formatter_updated.py .
COPY persistent_auth.py .
COPY examsoft_m365_config.py .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Update requirements.txt

Create/update `requirements.txt`:
```
streamlit>=1.25.0
pandas>=1.5.0
requests>=2.28.0
python-docx>=0.8.11
striprtf>=0.0.26
msal>=1.20.0
requests-oauthlib>=1.3.0
office365-rest-python-client>=2.5.0
openpyxl>=3.1.0
```

## ☁️ Azure Container Registry (ACR) Deployment

### 3. Build and Push to ACR

```bash
# Login to Azure
az login

# Set deployment variables
RESOURCE_GROUP="examsoft-rg"
ACR_NAME="examsoftacr"
IMAGE_NAME="examsoft-formatter"
TAG="v2.0"
LOCATION="eastus"

# Create resource group if not exists
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR if not exists
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --location $LOCATION

# Build and push image to ACR
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$TAG \
  --file Dockerfile \
  .

# Verify image was pushed
az acr repository list --name $ACR_NAME --output table
```

## 🌐 Azure Container Instance (ACI) Deployment

### 4. Deploy to ACI

```bash
# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create container instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG \
  --cpu 1 \
  --memory 2 \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --dns-name-label examsoft-formatter-v2 \
  --ports 8501 \
  --environment-variables \
    M365_CLIENT_ID="4848a7e9-327a-49ff-a789-6f8b928615b7" \
    M365_TENANT_ID="40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078" \
    M365_AUTHORITY="https://login.microsoftonline.com/40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078" \
    M365_REDIRECT_URI="https://examsoft-formatter-v2.eastus.azurecontainer.io"

# Get deployment status
az container show \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" \
  --output table
```

### 5. Update App Registration

```bash
# Update app registration with new redirect URI
az ad app update \
  --id 4848a7e9-327a-49ff-a789-6f8b928615b7 \
  --web-redirect-uris \
    "http://localhost:8501" \
    "https://examsoft-formatter-v2.eastus.azurecontainer.io"

# Verify redirect URIs were added
az ad app show \
  --id 4848a7e9-327a-49ff-a789-6f8b928615b7 \
  --query "web.redirectUris" \
  --output table
```

## 🔧 Application Configuration

### 6. Verify Microsoft 365 Permissions

Ensure these permissions are granted in Azure Portal:

**Required Permissions:**
- ✅ `User.Read` (Delegated)
- ✅ `Sites.Read.All` (Delegated)
- ✅ `Sites.ReadWrite.All` (Delegated)
- ✅ `Mail.Send` (Delegated)

**Grant Admin Consent URL:**
```
https://login.microsoftonline.com/40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078/adminconsent?client_id=4848a7e9-327a-49ff-a789-6f8b928615b7&state=12345&redirect_uri=https://localhost
```

## 🧪 Testing & Validation

### 7. Post-Deployment Testing

```bash
# Get application URL
APP_URL=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --query "ipAddress.fqdn" \
  --output tsv)

echo "Application URL: https://$APP_URL"

# Test application health
curl -f "https://$APP_URL/_stcore/health" && echo "✅ Application is healthy"

# View application logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2
```

### 8. Feature Testing Checklist

**Test these features after deployment:**

- [ ] **Authentication**: Sign in with Microsoft 365
- [ ] **Text Paste Method**: Copy/paste questions and instructions
- [ ] **File Upload Method**: Upload docx, rtf, txt, csv, xlsx files
- [ ] **Auto Parsing**: Upload combined instruction+question files
- [ ] **SharePoint Sites**: Verify dynamic site loading
- [ ] **Folder Browser**: Navigate folder tree and save favorites
- [ ] **File Upload**: Upload to selected SharePoint folder
- [ ] **Email Notifications**: Send test email notifications
- [ ] **Download Files**: Download generated RTF and DOCX files

## 🔄 Updates & Maintenance

### 9. Updating the Application

```bash
# Build and push new version
NEW_TAG="v2.1"
az acr build --registry $ACR_NAME --image $IMAGE_NAME:$NEW_TAG .

# Update container instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2-1 \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$NEW_TAG \
  [... same parameters as above ...]

# Delete old container
az container delete \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --yes
```

### 10. Monitoring & Logs

```bash
# View real-time logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --follow

# Monitor resource usage
az container show \
  --resource-group $RESOURCE_GROUP \
  --name examsoft-formatter-v2 \
  --query "containers[0].resources" \
  --output table
```

## 🎯 Final Application URL

**Production URL:** `https://examsoft-formatter-v2.eastus.azurecontainer.io`

## 📊 Architecture Summary

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Law Faculty   │────│  Streamlit App   │────│  SharePoint     │
│   (Users)       │    │  (ACI)          │    │  (File Storage) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │  Microsoft       │
                       │  Graph API       │
                       │  (Auth & Email)  │
                       └──────────────────┘
```

## 🆘 Troubleshooting

**Common Issues:**

1. **Authentication fails**: Check redirect URI in app registration
2. **SharePoint access denied**: Verify Sites permissions granted
3. **Email not working**: Ensure Mail.Send permission and user sign out/in
4. **Container won't start**: Check logs with `az container logs`
5. **File upload fails**: Verify ACR credentials and image build

**Support Contacts:**
- **Azure Issues**: Check Azure Portal > Resource Health
- **Microsoft 365**: Verify app registration permissions
- **Application Issues**: Check container logs for detailed errors