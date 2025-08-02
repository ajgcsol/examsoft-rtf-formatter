# Systems Administrator Maintenance Guide

## Overview

This guide provides comprehensive instructions for maintaining the ExamSoft RTF Formatter application in production.

## Production Environment

### Current Deployment
- **Application URL**: http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501
- **Azure Container Registry**: examsoftacr202508022041.azurecr.io
- **Container Instance**: examsoft-streamlit-1754167662
- **Resource Group**: examsoft-rg-202508022041
- **Current Version**: v10

### Architecture
```
Internet → Azure Container Instance → Streamlit App
                ↓
        Azure Container Registry (Docker Images)
                ↓
        Microsoft Graph API (SharePoint/Authentication)
```

## Regular Maintenance Tasks

### Daily Monitoring

#### 1. Application Health Check
```bash
# Check container status
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --query instanceView.state

# Test application endpoint
curl -f http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501/_stcore/health

# Check logs
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041
```

#### 2. Resource Usage
```bash
# Check container resource usage
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --query containers[0].resources
```

### Weekly Tasks

#### 1. Security Updates
```bash
# Check for base image updates
az acr repository show-tags --name examsoftacr202508022041 --repository examsoft-rtf-formatter

# Rebuild with latest base image (if needed)
cd utils/deployment
./deploy-acr-build.sh
./update-aci.sh
```

#### 2. Backup Verification
- Verify git repository is up to date
- Check Azure resource backup status
- Test SharePoint integration functionality

### Monthly Tasks

#### 1. Certificate and Token Management
- Review Microsoft 365 app registration certificates
- Check authentication token expiration settings
- Verify SharePoint permissions are still valid

#### 2. Performance Review
- Analyze container logs for errors
- Review user feedback
- Check resource utilization trends

## Deployment Procedures

### Standard Deployment
```bash
# Navigate to deployment utilities
cd utils/deployment

# Build new version (increments version automatically)
./deploy-acr-build.sh

# Update running container with new version
./update-aci.sh
```

### Emergency Rollback
```bash
# List available versions
az acr repository show-tags --name examsoftacr202508022041 --repository examsoft-rtf-formatter

# Edit update script to use previous version
vim utils/deployment/update-aci.sh
# Change NEW_TAG="v10" to previous version like NEW_TAG="v9"

# Deploy previous version
cd utils/deployment
./update-aci.sh
```

### Zero-Downtime Deployment
```bash
# Create new container instance with different name
az container create \
    --resource-group examsoft-rg-202508022041 \
    --name examsoft-streamlit-new \
    --image examsoftacr202508022041.azurecr.io/examsoft-rtf-formatter:v11 \
    --dns-name-label examsoft-streamlit-new \
    --ports 8501

# Test new instance
curl -f http://examsoft-streamlit-new.eastus.azurecontainer.io:8501/_stcore/health

# Update DNS/load balancer to point to new instance
# Delete old instance
az container delete --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --yes
```

## Troubleshooting

### Container Won't Start

#### Check Container Events
```bash
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --query instanceView.events
```

#### Common Issues
1. **Image Pull Errors**: Check ACR credentials and image exists
2. **Port Conflicts**: Verify port 8501 is available
3. **Resource Limits**: Check if container needs more CPU/memory

#### Solutions
```bash
# Restart container
az container restart --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041

# Recreate container with more resources
az container delete --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --yes
# Then run update-aci.sh with modified resource limits
```

### Authentication Issues

#### Microsoft 365 App Registration
1. **Check App Registration Status**
   - Login to Azure Portal
   - Navigate to Azure Active Directory > App registrations
   - Find ExamSoft RTF Formatter app
   - Verify certificates/secrets haven't expired

2. **SharePoint Permissions**
   - Check API permissions are granted and consented
   - Verify Sites.ReadWrite.All and Files.ReadWrite.All permissions
   - Re-grant admin consent if needed

#### Common Auth Errors
- **Token Expired**: Users need to sign out and sign back in
- **Insufficient Permissions**: Check app registration permissions
- **Redirect URI Mismatch**: Update redirect URIs in app registration

### SharePoint Upload Failures

#### Diagnostic Steps
```bash
# Run SharePoint diagnostic tool
python utils/development/sharepoint_debug_upload.py

# Test site discovery
python utils/development/site_discovery_test.py
```

#### Common Issues
1. **Path Not Found**: Verify SharePoint folder structure
2. **Permission Denied**: Check user and app permissions
3. **File Size Limits**: SharePoint has upload size restrictions

### Performance Issues

#### Memory Issues
```bash
# Check container memory usage
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --query containers[0].resources

# Increase memory allocation in update-aci.sh
# Change --memory 2 to --memory 4
```

#### CPU Issues
```bash
# Increase CPU allocation
# Change --cpu 1 to --cpu 2 in update-aci.sh
```

## Monitoring and Alerts

### Log Analysis
```bash
# Real-time log monitoring
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 --follow

# Error pattern search
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 | grep -i error

# Authentication errors
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041 | grep -i "auth\|token"
```

### Setting Up Alerts
```bash
# Create availability alert
az monitor metrics alert create \
    --name "ExamSoft App Down" \
    --resource-group examsoft-rg-202508022041 \
    --scopes /subscriptions/f5c85e55-7fca-4e2d-8527-14c2d008ab83/resourceGroups/examsoft-rg-202508022041/providers/Microsoft.ContainerInstance/containerGroups/examsoft-streamlit-1754167662 \
    --condition "avg 'Logs' < 1" \
    --window-size 5m \
    --evaluation-frequency 1m
```

## Security Maintenance

### Regular Security Tasks

#### 1. Credential Rotation
- Rotate Azure service principal secrets quarterly
- Update Microsoft 365 app registration certificates annually
- Review and rotate any API keys

#### 2. Access Review
- Review who has access to Azure resources
- Audit Microsoft 365 app permissions
- Check SharePoint folder permissions

#### 3. Security Scanning
```bash
# Scan Docker image for vulnerabilities
az acr check-health --name examsoftacr202508022041

# Check for outdated dependencies
cd streamlit-app
pip list --outdated
```

### Incident Response

#### Security Incident
1. **Immediate Actions**
   - Disable affected Azure resources
   - Revoke compromised credentials
   - Enable additional logging

2. **Investigation**
   - Review Azure activity logs
   - Check application logs for suspicious activity
   - Audit Microsoft 365 sign-in logs

3. **Recovery**
   - Deploy clean container image
   - Rotate all credentials
   - Update security configurations

## Backup and Recovery

### Code Backup
- Primary: Git repository
- Secondary: Azure DevOps or GitHub backup
- Configuration: Export Azure resource templates

### Configuration Backup
```bash
# Export Azure resources
az group export --name examsoft-rg-202508022041 --output-format json

# Backup container registry
az acr export --name examsoftacr202508022041 --repository examsoft-rtf-formatter
```

### Disaster Recovery
1. **Complete Environment Recreation**
   ```bash
   # Create new resource group
   az group create --name examsoft-rg-backup --location eastus
   
   # Deploy from backup
   cd utils/deployment
   # Update scripts with new resource group name
   ./deploy-acr-build.sh
   ./update-aci.sh
   ```

2. **Data Recovery**
   - SharePoint files are automatically backed up by Microsoft 365
   - Application state is stateless (no local data to recover)

## Contact Information

### Escalation Contacts
- **Primary**: Charleston School of Law IT Department
- **Azure Support**: Create support ticket in Azure Portal
- **Microsoft 365 Support**: Admin center support

### Vendor Contacts
- **Azure**: support.azure.com
- **Microsoft 365**: admin.microsoft.com/support
- **Docker**: support.docker.com

## Documentation Updates

When making changes:
1. Update this maintenance guide
2. Update developer documentation
3. Create deployment notes
4. Update README.md
5. Document configuration changes

## Useful Commands Reference

```bash
# Container management
az container list --resource-group examsoft-rg-202508022041
az container show --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041
az container logs --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041
az container restart --name examsoft-streamlit-1754167662 --resource-group examsoft-rg-202508022041

# Registry management
az acr list --resource-group examsoft-rg-202508022041
az acr repository list --name examsoftacr202508022041
az acr repository show-tags --name examsoftacr202508022041 --repository examsoft-rtf-formatter

# Resource group management
az group show --name examsoft-rg-202508022041
az resource list --resource-group examsoft-rg-202508022041

# Health checks
curl -f http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501/_stcore/health
curl -I http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501
```