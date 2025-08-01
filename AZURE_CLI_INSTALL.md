# Azure CLI Installation Guide

## 🔧 **Manual Installation Steps**

### **Option 1: Download MSI Installer (Recommended)**

1. **Download Azure CLI**:
   - Go to: https://aka.ms/installazurecliwindows
   - This will download `AzureCLI.msi`

2. **Run Installer**:
   - Double-click the downloaded MSI file
   - Follow the installation wizard
   - Accept the license agreement
   - Choose installation location (default is fine)
   - Click "Install"

3. **Verify Installation**:
   - Open a new Command Prompt or PowerShell
   - Run: `az --version`
   - You should see Azure CLI version information

### **Option 2: PowerShell Installation**

```powershell
# Run PowerShell as Administrator
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/i AzureCLI.msi /quiet'
```

### **Option 3: Chocolatey (if you have Chocolatey installed)**

```powershell
choco install azure-cli
```

### **Option 4: Microsoft Store**

- Search for "Azure CLI" in Microsoft Store
- Click "Get" to install

## 🔍 **Troubleshooting PATH Issues**

If `az` command is not recognized after installation:

### **Check Installation Path**
Common Azure CLI locations:
- `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin`
- `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin`

### **Add to PATH Manually**

1. **Open System Properties**:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click "Environment Variables"

2. **Edit PATH**:
   - Under "System Variables", find and select "Path"
   - Click "Edit"
   - Click "New"
   - Add the Azure CLI path (from above)
   - Click "OK" to save

3. **Restart Terminal**:
   - Close all Command Prompt/PowerShell windows
   - Open a new one and test: `az --version`

### **Alternative: Add to PATH via PowerShell**

```powershell
# Run as Administrator
$azPath = "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($currentPath -notlike "*$azPath*") {
    [Environment]::SetEnvironmentVariable("Path", $currentPath + ";" + $azPath, "Machine")
    Write-Host "Azure CLI added to PATH. Please restart your terminal."
}
```

## ✅ **Verify Installation**

After installation and PATH configuration:

```bash
# Check version
az --version

# Login to Azure
az login

# Verify authentication
az account show
```

## 🎯 **Next Steps**

Once Azure CLI is working:

1. **Authenticate**: `az login`
2. **Deploy**: `.\deploy-to-azure.ps1`
3. **Enjoy**: Your ExamSoft converter will be running in Azure!

## 🆘 **Still Having Issues?**

1. **Restart your computer** - This ensures PATH changes take effect
2. **Try running as Administrator** - Some operations require elevated privileges
3. **Check Windows Updates** - Ensure your system is up to date
4. **Disable antivirus temporarily** - Some antivirus software blocks installations

---

**Need help?** Check the official documentation: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
