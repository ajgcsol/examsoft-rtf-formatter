#!/bin/bash
# Azure CLI Script to set up SharePoint integration for ExamSoft Formatter
# Run this script as an Azure AD administrator

set -e  # Exit on any error

echo "🚀 Setting up ExamSoft Formatter SharePoint Integration..."
echo ""

# Configuration variables
APP_NAME="ExamSoft Formatter"
REDIRECT_URI="http://localhost:8501"
TENANT_DOMAIN="charlestonlaw.edu"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  App Name: $APP_NAME"
echo "  Redirect URI: $REDIRECT_URI"
echo "  Tenant: $TENANT_DOMAIN"
echo ""

# Check if user is logged in to Azure CLI
echo -e "${BLUE}🔍 Checking Azure CLI login status...${NC}"
if ! az account show > /dev/null 2>&1; then
    echo -e "${RED}❌ Not logged in to Azure CLI${NC}"
    echo "Please run: az login"
    exit 1
fi

echo -e "${GREEN}✅ Azure CLI authenticated${NC}"

# Get tenant ID
echo -e "${BLUE}🔍 Getting tenant information...${NC}"
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "  Tenant ID: $TENANT_ID"

# Step 1: Create app registration
echo ""
echo -e "${BLUE}📝 Step 1: Creating app registration...${NC}"

APP_REGISTRATION=$(az ad app create \
    --display-name "$APP_NAME" \
    --web-redirect-uris "$REDIRECT_URI" \
    --sign-in-audience "AzureADMyOrg" \
    --query "{appId:appId,objectId:id}" \
    --output json)

APP_ID=$(echo $APP_REGISTRATION | jq -r '.appId')
OBJECT_ID=$(echo $APP_REGISTRATION | jq -r '.objectId')

echo -e "${GREEN}✅ App registration created${NC}"
echo "  App ID (Client ID): $APP_ID"
echo "  Object ID: $OBJECT_ID"

# Step 2: Create service principal
echo ""
echo -e "${BLUE}🔑 Step 2: Creating service principal...${NC}"

SERVICE_PRINCIPAL=$(az ad sp create --id $APP_ID --query "id" --output tsv)
echo -e "${GREEN}✅ Service principal created${NC}"
echo "  Service Principal ID: $SERVICE_PRINCIPAL"

# Step 3: Add required API permissions
echo ""
echo -e "${BLUE}🛡️  Step 3: Adding Microsoft Graph API permissions...${NC}"

# Microsoft Graph API ID
GRAPH_API_ID="00000003-0000-0000-c000-000000000000"

# Permission IDs for Microsoft Graph
SITES_READWRITE_ALL="89fe6a52-be36-487e-b7d8-d061c450a026"  # Sites.ReadWrite.All (Application)
FILES_READWRITE_ALL="75359482-378d-4052-8f01-80520e7db3cd"   # Files.ReadWrite.All (Application)
USER_READ="e1fe6dd8-ba31-4d61-89e7-88639da4683d"             # User.Read (Delegated)

# Add application permissions
echo "  Adding Sites.ReadWrite.All (Application)..."
az ad app permission add \
    --id $APP_ID \
    --api $GRAPH_API_ID \
    --api-permissions $SITES_READWRITE_ALL=Role

echo "  Adding Files.ReadWrite.All (Application)..."
az ad app permission add \
    --id $APP_ID \
    --api $GRAPH_API_ID \
    --api-permissions $FILES_READWRITE_ALL=Role

echo "  Adding User.Read (Delegated)..."
az ad app permission add \
    --id $APP_ID \
    --api $GRAPH_API_ID \
    --api-permissions $USER_READ=Scope

echo -e "${GREEN}✅ API permissions added${NC}"

# Step 4: Grant admin consent (with retry logic)
echo ""
echo -e "${BLUE}🔓 Step 4: Granting admin consent...${NC}"

# Wait longer for permissions to propagate
echo -e "${YELLOW}  Waiting for permissions to propagate...${NC}"
sleep 15

CONSENT_ATTEMPTS=0
MAX_CONSENT_ATTEMPTS=3
CONSENT_SUCCESS=false

while [ $CONSENT_ATTEMPTS -lt $MAX_CONSENT_ATTEMPTS ] && [ "$CONSENT_SUCCESS" = false ]; do
    CONSENT_ATTEMPTS=$((CONSENT_ATTEMPTS + 1))
    echo -e "${YELLOW}  Consent attempt $CONSENT_ATTEMPTS of $MAX_CONSENT_ATTEMPTS...${NC}"
    
    if az ad app permission admin-consent --id $APP_ID 2>/dev/null; then
        CONSENT_SUCCESS=true
        echo -e "${GREEN}✅ Admin consent granted${NC}"
    else
        if [ $CONSENT_ATTEMPTS -lt $MAX_CONSENT_ATTEMPTS ]; then
            echo -e "${YELLOW}  Consent failed, waiting 10 seconds before retry...${NC}"
            sleep 10
        else
            echo -e "${YELLOW}⚠️  Admin consent failed after $MAX_CONSENT_ATTEMPTS attempts${NC}"
            echo -e "${YELLOW}  You can grant consent manually in Azure Portal:${NC}"
            echo -e "${YELLOW}  1. Go to Azure Portal > Azure Active Directory > App registrations${NC}"
            echo -e "${YELLOW}  2. Find '$APP_NAME' app${NC}"
            echo -e "${YELLOW}  3. Go to API permissions${NC}"
            echo -e "${YELLOW}  4. Click 'Grant admin consent for Charleston School of Law'${NC}"
        fi
    fi
done

# Step 5: Create client secret
echo ""
echo -e "${BLUE}🔐 Step 5: Creating client secret...${NC}"

SECRET_NAME="ExamSoft-Formatter-Secret"
SECRET_EXPIRY="2026-12-31"  # 2+ years from now

CLIENT_SECRET=$(az ad app credential reset \
    --id $APP_ID \
    --display-name "$SECRET_NAME" \
    --end-date "$SECRET_EXPIRY" \
    --query "password" \
    --output tsv)

echo -e "${GREEN}✅ Client secret created${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Save this client secret - it won't be shown again!${NC}"

# Step 6: Generate configuration
echo ""
echo -e "${BLUE}📄 Step 6: Generating application configuration...${NC}"

cat > examsoft_m365_config.py << EOF
# ExamSoft Formatter - Microsoft 365 Configuration
# Generated on $(date)
# 
# SECURITY NOTE: Keep the client_secret secure and do not commit to version control

M365_CONFIG = {
    "client_id": "$APP_ID",
    "client_secret": "$CLIENT_SECRET",  # KEEP THIS SECURE!
    "tenant_id": "$TENANT_DOMAIN",
    "authority": "https://login.microsoftonline.com/$TENANT_DOMAIN",
    "scope": [
        "https://graph.microsoft.com/Sites.ReadWrite.All", 
        "https://graph.microsoft.com/Files.ReadWrite.All",
        "https://graph.microsoft.com/User.Read"
    ],
    "redirect_uri": "$REDIRECT_URI"
}

# Azure AD App Registration Details
APP_REGISTRATION_INFO = {
    "app_name": "$APP_NAME",
    "app_id": "$APP_ID", 
    "object_id": "$OBJECT_ID",
    "tenant_id": "$TENANT_ID",
    "service_principal_id": "$SERVICE_PRINCIPAL",
    "created_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo -e "${GREEN}✅ Configuration file created: examsoft_m365_config.py${NC}"

# Step 7: Summary and next steps
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  App Name: $APP_NAME"
echo "  Client ID: $APP_ID"
echo "  Tenant: $TENANT_DOMAIN"
echo "  Secret Expires: $SECRET_EXPIRY"
echo ""
echo -e "${BLUE}📁 Files Created:${NC}"
echo "  📄 examsoft_m365_config.py - Configuration for your application"
echo ""
echo -e "${YELLOW}⚠️  SECURITY REMINDERS:${NC}"
echo "  🔐 Keep the client secret secure"
echo "  📝 Do not commit secrets to version control"
echo "  🔄 Set up secret rotation before expiry ($SECRET_EXPIRY)"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "  1. Copy the configuration from examsoft_m365_config.py"
echo "  2. Update M365_CONFIG in examsoft_formatter_updated.py"
echo "  3. Test the SharePoint integration"
echo "  4. Deploy to your users"
echo ""
echo -e "${GREEN}✅ ExamSoft Formatter SharePoint integration is ready!${NC}"
