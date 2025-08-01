import requests
from urllib.parse import quote

def upload_to_sharepoint_exam_procedures(access_token, file_content, filename):
    """
    Upload file directly to Exam Procedures site / ExamSoft / Import folder
    Site: "Exam Procedures" (with space)
    Site ID: b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip
    Folder: /ExamSoft/Import
    """
    
    # The correct site ID provided by user
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    # Folder path: ExamSoft/Import
    folder_path = "ExamSoft/Import"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }
    
    try:
        # Validate inputs
        if not access_token:
            return False, "No access token provided"
        
        if not file_content:
            return False, "No file content provided"
        
        if not filename:
            return False, "No filename provided"
        
        # Build the upload URL using the site root path
        encoded_filename = quote(filename)
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{encoded_filename}:/content"
        
        print(f"🔍 Upload attempt:")
        print(f"   📁 Site ID: {site_id}")
        print(f"   📂 Folder: {folder_path}")
        print(f"   📄 Filename: {filename}")
        print(f"   📄 Encoded: {encoded_filename}")
        print(f"   🔗 URL: {upload_url}")
        print(f"   📊 Content type: {type(file_content)}")
        print(f"   📏 Content size: {len(file_content) if hasattr(file_content, '__len__') else 'unknown'}")
        
        # Convert content to bytes if needed
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
            print(f"   🔄 Converted string to bytes: {len(file_content)} bytes")
        elif hasattr(file_content, 'read'):
            file_content = file_content.read()
            print(f"   🔄 Read from file object: {len(file_content)} bytes")
        
        # Upload the file
        response = requests.put(upload_url, headers=headers, data=file_content)
        
        print(f"📤 Upload response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            file_size = response_data.get('size', len(file_content) if isinstance(file_content, bytes) else 0)
            
            print(f"✅ Upload successful!")
            print(f"🔗 File URL: {file_url}")
            print(f"📊 File size: {file_size} bytes")
            
            return True, {
                'url': file_url,
                'size': file_size,
                'created': response_data.get('createdDateTime', 'N/A'),
                'message': f'Successfully uploaded to Exam Procedures / ExamSoft / Import'
            }
        else:
            error_msg = f"Upload failed with status {response.status_code}"
            try:
                error_data = response.json()
                error_details = error_data.get('error', {})
                error_msg += f": {error_details.get('message', 'Unknown error')}"
                print(f"❌ Error details: {error_data}")
            except:
                error_msg += f": {response.text}"
                print(f"❌ Error text: {response.text}")
            
            return False, error_msg
            
    except Exception as e:
        print(f"❌ Exception during upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Upload error: {str(e)}"

# Alternative function that tries to create the folder if it doesn't exist
def upload_to_sharepoint_with_folder_creation(access_token, file_content, filename):
    """
    Upload file to Exam Procedures / ExamSoft / Import with folder creation if needed
    """
    
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # First, try to ensure the ExamSoft folder exists
        examsoft_folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft"
        examsoft_response = requests.get(examsoft_folder_url, headers=headers)
        
        if examsoft_response.status_code == 404:
            # Create ExamSoft folder
            create_folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
            folder_data = {
                "name": "ExamSoft",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_folder_url, headers=headers, json=folder_data)
            print(f"📁 Created ExamSoft folder: {create_response.status_code}")
        
        # Then, try to ensure the Import folder exists inside ExamSoft
        import_folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft/Import"
        import_response = requests.get(import_folder_url, headers=headers)
        
        if import_response.status_code == 404:
            # Create Import folder inside ExamSoft
            create_import_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft:/children"
            import_folder_data = {
                "name": "Import",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_import_response = requests.post(create_import_url, headers=headers, json=import_folder_data)
            print(f"📁 Created Import folder: {create_import_response.status_code}")
        
        # Now upload the file
        return upload_to_sharepoint_exam_procedures(access_token, file_content, filename)
        
    except Exception as e:
        print(f"❌ Exception during folder creation: {str(e)}")
        # Fall back to direct upload
        return upload_to_sharepoint_exam_procedures(access_token, file_content, filename)
