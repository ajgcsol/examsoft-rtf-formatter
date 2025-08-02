# ExamSoft RTF Formatter - Streamlit App

This directory contains the containerized Streamlit application for the ExamSoft RTF Formatter.

## Files

- `streamlit_app.py` - Main entry point for the Streamlit application
- `examsoft_formatter_updated.py` - Core application logic and UI
- `sharepoint_integration_fixed.py` - SharePoint upload functionality
- `persistent_auth.py` - Microsoft 365 authentication handling
- `examsoft_m365_config.py` - Microsoft 365 app registration configuration
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition for Azure deployment
- `.dockerignore` - Files to exclude from Docker build

## Local Testing

To test the Docker container locally:

```bash
# Build the image
docker build -t examsoft-streamlit .

# Run the container
docker run -p 8501:8501 examsoft-streamlit

# Access the app
open http://localhost:8501
```

## Azure Deployment

This directory is automatically used by the Azure deployment scripts:

- `../deploy-streamlit-to-azure.sh` - Full deployment script
- `../quick-deploy-streamlit.sh` - Quick redeployment script

## Configuration

The Microsoft 365 configuration will be automatically updated during Azure deployment to match your tenant settings.

## Security

- The container runs as a non-root user
- No secrets are baked into the image
- Configuration is handled via environment variables in Azure
