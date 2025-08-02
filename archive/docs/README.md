# ExamSoft RTF Formatter

A Streamlit application that formats RTF exam files for ExamSoft import with Microsoft 365 SharePoint integration and Azure LibreOffice conversion service.

---

## Features
- **RTF Formatting**: Converts Word documents to properly formatted RTF files for ExamSoft
- **Azure LibreOffice Integration**: Uses Azure Container Instance for reliable document conversion
- **SharePoint Upload**: Automatically uploads formatted files to SharePoint with persistent authentication
- **90-Day Authentication**: Long-term authentication persistence for seamless user experience
- **Answer Key Processing**: Handles Excel answer key files and integrates with RTF output
- **Streamlit Cloud Deployment**: Ready for cloud deployment with configuration files

## Architecture
- **Frontend**: Streamlit web application
- **Document Conversion**: Azure Container Instance running LibreOffice at 4.156.115.147:5000
- **Authentication**: Microsoft 365 MSAL with device code flow (90-day persistence)
- **Storage**: SharePoint integration via Microsoft Graph API
- **Deployment**: Streamlit Cloud ready
- Cloud-ready: deploy conversion service to Azure Container Instances

---

## Local Setup

### 1. Install Requirements
- Python 3.11+
- [Streamlit](https://streamlit.io/):
  ```sh
  pip install streamlit pandas python-docx requests
  ```
- (Optional) LibreOffice for local conversion
- (Optional) Docker Desktop for running the conversion service

### 2. Run Streamlit App
```sh
streamlit run examsoft_formatter_updated.py
```
- App will open at [http://localhost:8501](http://localhost:8501)

### 3. (Optional) Run LibreOffice Docker Conversion Service Locally

#### Build the Docker image:
```sh
docker build -t libreoffice-converter .
```

#### Run the container:
```sh
docker run -p 8080:8080 libreoffice-converter
```
- The conversion API will be available at [http://localhost:8080/convert](http://localhost:8080/convert)

---

## Cloud Deployment (Azure Example)

### 1. Push Docker Image to Docker Hub
```sh
docker tag libreoffice-converter <your-dockerhub-username>/libreoffice-converter:latest
docker push <your-dockerhub-username>/libreoffice-converter:latest
```

### 2. Deploy to Azure Container Instances
```sh
az container create \
  --resource-group <your-resource-group> \
  --name libreoffice-converter \
  --image <your-dockerhub-username>/libreoffice-converter:latest \
  --ports 8080 \
  --dns-name-label <unique-dns-name> \
  --environment-variables FLASK_ENV=production
```
- The API will be available at:  
  `http://<unique-dns-name>.<region>.azurecontainer.io:8080/convert`

### 3. Update Streamlit App to Use Cloud API
- In the app, set the API URL to the Azure endpoint (or use the UI field):
  ```python
  api_url = "http://<unique-dns-name>.<region>.azurecontainer.io:8080/convert"
  ```

### 4. (Optional) Deploy Streamlit App to Azure
- You can deploy Streamlit to Azure Web Apps, Azure Container Apps, or Streamlit Community Cloud.
- For Azure Web Apps:
  ```sh
  az webapp up --name <your-streamlit-app-name> --resource-group <your-resource-group> --runtime "PYTHON:3.11"
  ```

---

## Usage
1. Start the Docker conversion service (locally or in the cloud).
2. Run the Streamlit app.
3. Paste your exam content and answer key.
4. Select the conversion method (local, API, or GroupDocs).
5. Download the formatted RTF for ExamSoft import.

---

## Streamlit Cloud Deployment

### Prerequisites
- Microsoft 365 App Registration with required permissions
- Azure Container Instance running LibreOffice service
- GitHub repository

### Deployment Steps

1. **Push to GitHub**:
```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

2. **Configure Streamlit Cloud**:
   - Connect your GitHub repository to Streamlit Cloud
   - Set the main file path to `streamlit_app.py`

3. **Configure Secrets**:
   Copy the template from `streamlit_secrets_template.toml` and add to Streamlit Cloud secrets:
   ```toml
   [M365]
   M365_CLIENT_ID = "4848a7e9-327a-49ff-a789-6f8b928615b7"
   M365_TENANT_ID = "charlestonlaw.edu"
   M365_AUTHORITY = "https://login.microsoftonline.com/charlestonlaw.edu"
   
   [AZURE]
   AZURE_LIBREOFFICE_ENDPOINT = "http://4.156.115.147:5000"
   ```

4. **Update App Registration**:
   Add your Streamlit Cloud URL to the app registration redirect URIs:
   - Go to Azure Portal > App Registrations > Your App
   - Add redirect URI: `https://your-app-name.streamlit.app`

### Configuration Files
- `streamlit_app.py` - Main entry point for cloud deployment
- `.streamlit/config.toml` - Theme and server configuration
- `streamlit_secrets_template.toml` - Template for Streamlit secrets
- `examsoft_m365_config.py` - Handles both local and cloud configuration

---

## API Test Example (Python)
```python
import requests
with open('yourfile.docx', 'rb') as f:
    r = requests.post('http://localhost:8080/convert', files={'file': f})
    with open('converted.rtf', 'wb') as out:
        out.write(r.content)
```

---

## Files
- `examsoft_formatter_updated.py` — Main Streamlit app
- `Dockerfile` — For the LibreOffice conversion service
- `convert_service.py` — Flask API for DOCX-to-RTF conversion
- `requirements.txt` — Python dependencies for the Docker service

---

## Troubleshooting
- Make sure Docker is running before building/running the container.
- If deploying to Azure, ensure your image is pushed to a public or authenticated registry.
- Update API URLs in the Streamlit app as needed.

---

## Credits
- Built with Python, Streamlit, Flask, LibreOffice, and Docker.
