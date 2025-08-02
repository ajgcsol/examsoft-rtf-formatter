# Developer Setup Guide

## Prerequisites

- Python 3.11+
- Git
- Docker (optional, for local testing)
- Azure CLI (for deployment)
- Visual Studio Code or similar IDE

## Local Development Setup

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd examsoft-rtf-formatter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd streamlit-app
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.streamlit/secrets.toml` in the streamlit-app directory:

```toml
# Copy from streamlit_secrets_template.toml and fill in values
[azure]
client_id = "your-app-registration-client-id"
tenant_id = "your-tenant-id"
client_secret = "your-client-secret"

[sharepoint]
site_url = "https://charlestonlaw.sharepoint.com/sites/IT"
folder_path = "Shared Documents/ExamSoft/File-converter/Import"
```

### 3. Run Development Server

```bash
cd streamlit-app
streamlit run streamlit_app.py
```

Application will be available at `http://localhost:8501`

## Code Structure

### Main Application (`streamlit-app/`)

- **`streamlit_app.py`**: Main Streamlit application with UI
- **`examsoft_formatter_updated.py`**: Core formatting and processing logic
- **`persistent_auth.py`**: Microsoft 365 authentication handling
- **`sharepoint_integration_fixed.py`**: SharePoint upload functionality
- **`safe_formatter.py`**: Safe import wrapper for formatter functions

### Key Functions

#### Core Formatting
```python
# examsoft_formatter_updated.py
def parse_questions_from_text(questions_text, answer_key, use_asterisk_method=True)
def create_rtf_content(questions_list, answer_key=None, use_answer_key_method=False)
def parse_answer_key_with_header_detection(answer_key_text)
```

#### Authentication
```python
# persistent_auth.py
def initialize_persistent_auth()
def render_persistent_auth_ui()
def sign_out_persistent()
```

#### SharePoint Integration
```python
# sharepoint_integration_fixed.py
def upload_to_sharepoint_corrected(access_token, file_content, filename)
```

## Development Workflow

### 1. Making Changes

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes in `streamlit-app/` directory
3. Test locally with `streamlit run streamlit_app.py`
4. Run tests: `python utils/testing/test_imports.py`

### 2. Testing

#### Unit Tests
```bash
# Test imports and basic functionality
python utils/testing/test_imports.py
python utils/testing/simple_test.py
```

#### Integration Tests
```bash
# Test SharePoint integration
python utils/development/quick_sharepoint_test.py

# Test Azure authentication
python utils/development/simple_azure_test.py
```

#### Manual Testing Checklist
- [ ] Text paste method works
- [ ] File upload method works
- [ ] Answer key parsing handles headers correctly
- [ ] RTF generation produces valid ExamSoft format
- [ ] Microsoft 365 authentication works
- [ ] SharePoint upload succeeds
- [ ] Email notifications work (if configured)

### 3. Deployment Testing

```bash
# Build Docker image locally
docker build -t examsoft-test streamlit-app/

# Run container locally
docker run -p 8501:8501 examsoft-test

# Test container
curl http://localhost:8501/_stcore/health
```

## Code Standards

### Python Style
- Follow PEP 8
- Use type hints where applicable
- Add docstrings for functions
- Handle exceptions gracefully

### Streamlit Best Practices
- Use session state for persistent data
- Avoid `st.rerun()` in authentication flows
- Use `st.cache_data` for expensive operations
- Provide clear user feedback with success/error messages

### Security Guidelines
- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Sanitize file uploads
- Use HTTPS for all external API calls

## Debugging

### Common Issues

#### Authentication Problems
```python
# Check token status
import streamlit as st
st.write("Access token:", st.session_state.get('sp_access_token', 'None'))
st.write("Token expires:", st.session_state.get('token_expires_at', 'None'))
```

#### SharePoint Upload Issues
```python
# Debug upload path
python utils/development/sharepoint_debug_upload.py
```

#### Answer Key Parsing
```python
# Debug answer key detection
python utils/testing/debug_questions.py
```

### Development Tools

#### Available Utilities
- `utils/development/discover_sharepoint.py`: Explore SharePoint structure
- `utils/testing/diagnose_auth_config.py`: Check authentication setup
- `utils/testing/test_environment_detection.py`: Verify environment

## Contributing

1. Follow git flow: feature branches from main
2. Write tests for new functionality
3. Update documentation
4. Test deployment process
5. Submit pull request with clear description

## Performance Considerations

- Use `@st.cache_data` for expensive operations
- Minimize API calls in user interface
- Process large files in chunks
- Use session state efficiently
- Consider memory usage for file uploads

## Troubleshooting

### Module Import Errors
```bash
# Ensure all dependencies are installed
pip install -r streamlit-app/requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Streamlit Session Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Reset session state
# Add to app: st.session_state.clear()
```

### Azure CLI Issues
```bash
# Login to Azure
az login

# Check subscription
az account show

# Test ACR access
az acr login --name examsoftacr202508022041
```