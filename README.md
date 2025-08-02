# ExamSoft RTF Formatter v2.0

A comprehensive web application for converting exam questions and answer keys into ExamSoft RTF format, built for Charleston School of Law.

## 🚀 Quick Start

### For End Users
**Live Application:** http://examsoft-streamlit-1754167662.eastus.azurecontainer.io:8501

1. Open the application in your web browser
2. Click "🆘 Need Help?" for step-by-step guidance
3. Fill in course information (course code, section, professor)
4. Paste or upload your exam questions and answer key
5. Download the formatted RTF file for ExamSoft import

### For Developers
```bash
# Clone repository
git clone <repository-url>
cd examsoft-rtf-formatter

# Run locally
cd streamlit-app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📁 Repository Structure

```
examsoft-rtf-formatter/
├── streamlit-app/           # Main application code
│   ├── streamlit_app.py     # Main Streamlit application
│   ├── examsoft_formatter_updated.py  # Core formatting logic
│   ├── persistent_auth.py   # Microsoft 365 authentication
│   ├── sharepoint_integration*.py     # SharePoint upload functionality
│   └── requirements.txt     # Python dependencies
├── utils/                   # Utility scripts and tools
│   ├── deployment/          # Deployment scripts
│   ├── azure-setup/         # Azure configuration scripts
│   ├── development/         # Development and testing tools
│   └── testing/             # Testing utilities
├── docs/                    # Documentation
│   ├── development/         # Developer guides
│   ├── deployment/          # Deployment guides
│   └── maintenance/         # Maintenance documentation
└── archive/                 # Legacy files and backups
    ├── legacy-code/         # Old application versions
    ├── scripts/             # Old deployment scripts
    ├── docs/                # Archived documentation
    └── examples/            # Example files
```

## 🔧 Features

- **Dual Input Methods**: Text paste or file upload (Word, RTF, Excel)
- **Answer Key Processing**: Automatic header detection and validation
- **ExamSoft Formatting**: Proper RTF generation with answer key methods
- **Microsoft 365 Integration**: SharePoint upload and email notifications
- **User-Friendly Interface**: Step-by-step guidance for non-technical users
- **Azure Deployment**: Containerized deployment with Azure Container Registry

## 🛠 Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.11
- **Authentication**: Microsoft Graph API (MSAL)
- **File Processing**: pandas, python-docx, openpyxl
- **Deployment**: Docker, Azure Container Registry, Azure Container Instances
- **Document Conversion**: LibreOffice (via Docker API)

## 📖 Documentation

- [Developer Setup Guide](docs/development/DEVELOPER_SETUP.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)
- [Maintenance Guide](docs/maintenance/MAINTENANCE_GUIDE.md)
- [Azure Configuration](docs/deployment/AZURE_SETUP.md)

## 🔐 Security & Authentication

- Microsoft 365 integration for secure file uploads
- Token-based authentication with automatic refresh
- Azure App Registration for enterprise security
- HTTPS endpoints for secure data transmission

## 🚀 Deployment

### Current Production
- **Azure Container Registry**: `examsoftacr202508022041.azurecr.io`
- **Container Instance**: `examsoft-streamlit-1754167662`
- **Version**: v10 (latest)

### Quick Deploy
```bash
# Build and deploy new version
cd utils/deployment
./deploy-acr-build.sh
./update-aci.sh
```

## 🐛 Troubleshooting

Common issues and solutions are documented in the built-in help system. Click "🆘 Need Help?" in the application for guidance.

## 📞 Support

For technical support or feature requests:
- Contact Charleston School of Law IT Department
- Check the built-in help system for common issues
- Review documentation in the `docs/` directory

## 📄 License

Copyright © 2025 Charleston School of Law. All rights reserved.