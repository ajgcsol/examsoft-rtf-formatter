#!/bin/bash

# Fix Email Permissions for ExamSoft RTF Formatter
# This script adds the Mail.Send permission to the Azure app registration

APP_ID="4848a7e9-327a-49ff-a789-6f8b928615b7"
TENANT_ID="40acb9f6-d0e3-4a23-9fc1-23e8e1ac0078"

echo "🔧 Fixing Email Permissions for ExamSoft RTF Formatter"
echo "================================================="
echo ""

# Check if user is logged in to Azure CLI
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure CLI. Please run: az login"
    exit 1
fi

echo "✅ Azure CLI authenticated"

# Get Microsoft Graph service principal ID
GRAPH_SP_ID=$(az ad sp list --display-name "Microsoft Graph" --query '[0].id' -o tsv)
echo "📋 Microsoft Graph Service Principal ID: $GRAPH_SP_ID"

# Get Mail.Send permission ID
MAIL_SEND_PERMISSION=$(az ad sp show --id $GRAPH_SP_ID --query "appRoles[?value=='Mail.Send'].id" -o tsv)
echo "📧 Mail.Send Permission ID: $MAIL_SEND_PERMISSION"

if [ -z "$MAIL_SEND_PERMISSION" ]; then
    echo "❌ Could not find Mail.Send permission ID"
    exit 1
fi

echo ""
echo "🔄 Adding Mail.Send permission to app registration..."

# Add the Mail.Send permission to the app
az ad app permission add \
    --id $APP_ID \
    --api 00000003-0000-0000-c000-000000000000 \
    --api-permissions "${MAIL_SEND_PERMISSION}=Role"

if [ $? -eq 0 ]; then
    echo "✅ Mail.Send permission added successfully"
else
    echo "⚠️  Permission may already exist or there was an error"
fi

echo ""
echo "🔄 Granting admin consent..."

# Grant admin consent
az ad app permission admin-consent --id $APP_ID

if [ $? -eq 0 ]; then
    echo "✅ Admin consent granted successfully"
    echo ""
    echo "🎉 Email permissions should now work!"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Users may need to sign out and sign back in"
    echo "2. Test email functionality in the app"
    echo "3. If still not working, wait 5-10 minutes for permissions to propagate"
else
    echo "❌ Failed to grant admin consent"
    echo ""
    echo "🔗 Manual Admin Consent URL:"
    echo "https://login.microsoftonline.com/${TENANT_ID}/adminconsent?client_id=${APP_ID}&state=12345&redirect_uri=https://localhost"
    echo ""
    echo "📋 Manual Steps:"
    echo "1. Copy the URL above"
    echo "2. Open it in a browser as a Global Administrator"
    echo "3. Accept the permissions"
fi
