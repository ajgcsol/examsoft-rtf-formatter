# ExamSoft Formatter - Project Structure

This document outlines the current project structure and file organization.

## 🏗️ **Current Active Files** (Main Directory)

### **Core Application Files**
- `examsoft_formatter_updated.py` - **Main Streamlit application**
- `sharepoint_integration_fixed.py` - **SharePoint OAuth integration module**
- `azure_config_loader.py` - **Azure configuration and endpoint management**
- `convert_service.py` - **Docker/Flask API for LibreOffice conversion**

### **Configuration Files**
- `examsoft_m365_config.py` - **Microsoft 365 app registration config**
- `requirements.txt` - **Python dependencies**
- `Dockerfile` - **Container configuration for LibreOffice service**

### **Deployment Files**
- `deploy-to-azure.ps1` - **PowerShell Azure deployment script**
- `deploy-to-azure.sh` - **Bash Azure deployment script**
- `AZURE_DEPLOYMENT.md` - **Azure deployment guide**

### **Documentation**
- `README.md` - **Main project documentation**
- `SETUP_COMPLETE.md` - **Setup completion guide**

## 📁 **Utils Directory Structure**

### **`utils/setup/`** - Setup and Configuration Scripts
- Setup scripts for SharePoint integration
- App registration configuration scripts
- Environment setup utilities

### **`utils/legacy/`** - Deprecated/Old Versions
- Previous versions of the formatter
- Backup files and deprecated modules
- Historical development files

### **`utils/testing/`** - Development and Testing Files
- Test scripts for debugging
- Development utilities
- Conversion testing tools

### **`utils/samples/`** - Sample Files and Examples
- Example RTF and DOCX files
- Test data and templates
- Sample configurations

## 🗂️ **File Categories**

### **Keep in Root (Active Files)**
- Main application files actively used
- Current configuration files
- Primary deployment scripts
- Core documentation

### **Move to utils/setup/**
- SharePoint setup scripts
- App registration utilities
- Initial environment setup

### **Move to utils/legacy/**
- Old formatter versions
- Backup files
- Deprecated modules

### **Move to utils/testing/**
- Debug and test scripts
- Development utilities
- Conversion testing tools

### **Move to utils/samples/**
- Example files
- Test data
- Sample outputs

## 🎯 **Benefits of Organization**

✅ **Cleaner Root Directory**: Focus on active, production files  
✅ **Logical Grouping**: Related files organized together  
✅ **Easy Maintenance**: Clear separation of active vs utility files  
✅ **Better Navigation**: Developers can quickly find what they need  
✅ **Safer Updates**: Reduced risk of accidentally modifying wrong files  

## 📋 **Usage Guidelines**

- **Root Directory**: Only production-ready, actively used files
- **utils/setup/**: Run once during initial setup
- **utils/legacy/**: Reference only, do not modify
- **utils/testing/**: Development and debugging only
- **utils/samples/**: Examples and templates

---

**Last Updated**: August 2025  
**Structure Version**: 2.0
