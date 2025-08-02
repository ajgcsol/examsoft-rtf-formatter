import requests
from urllib.parse import quote
import streamlit as st

def test_sharepoint_access(access_token):
    """Test if we can access the SharePoint site"""
    
    site_id = "charlestonlaw.sharepoint.com,ba0b6d09-2f32-4ccf-a24d-9a41e9be4a6a,ffe7f195-f2eb-4f68-af47-35a01fa9a2d7"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        # Test 1: Can we access the site?
        site_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}"
        site_response = requests.get(site_url, headers=headers)
        
        print(f"🔍 Site access test: {site_response.status_code}")
        if site_response.status_code == 200:
            site_data = site_response.json()
            print(f"✅ Site found: {site_data.get('displayName', 'Unknown')}")
        else:
            print(f"❌ Site access failed: {site_response.text}")
            return False, f"Cannot access site: {site_response.status_code}"
        
        # Test 2: Can we access the drive?
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive"
        drive_response = requests.get(drive_url, headers=headers)
        
        print(f"🔍 Drive access test: {drive_response.status_code}")
        if drive_response.status_code == 200:
            drive_data = drive_response.json()
            print(f"✅ Drive found: {drive_data.get('name', 'Unknown')}")
            drive_id = drive_data.get('id')
        else:
            print(f"❌ Drive access failed: {drive_response.text}")
            return False, f"Cannot access drive: {drive_response.status_code}"
        
        # Test 3: Can we access the root folder?
        root_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root"
        root_response = requests.get(root_url, headers=headers)
        
        print(f"🔍 Root folder test: {root_response.status_code}")
        if root_response.status_code == 200:
            print(f"✅ Root folder accessible")
        else:
            print(f"❌ Root folder failed: {root_response.text}")
            return False, f"Cannot access root folder: {root_response.status_code}"
        
        # Test 4: List what's in the root
        children_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
        children_response = requests.get(children_url, headers=headers)
        
        print(f"🔍 Root children test: {children_response.status_code}")
        if children_response.status_code == 200:
            children_data = children_response.json()
            folders = [item['name'] for item in children_data.get('value', []) if item.get('folder')]
            files = [item['name'] for item in children_data.get('value', []) if not item.get('folder')]
            print(f"📁 Folders in root: {folders}")
            print(f"📄 Files in root: {files}")
        else:
            print(f"❌ Cannot list root children: {children_response.text}")
        
        return True, "Site access successful"
        
    except Exception as e:
        print(f"❌ Exception during site test: {str(e)}")
        return False, f"Exception: {str(e)}"

def create_folder_if_needed(access_token, site_id, folder_path):
    """Create folder structure if it doesn't exist"""
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Check if ExamSoft folder exists
        examsoft_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft"
        examsoft_response = requests.get(examsoft_url, headers=headers)
        
        if examsoft_response.status_code == 404:
            # Create ExamSoft folder
            print("📁 Creating ExamSoft folder...")
            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
            folder_data = {
                "name": "ExamSoft",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_url, headers=headers, json=folder_data)
            print(f"   Result: {create_response.status_code}")
            if create_response.status_code not in [200, 201]:
                print(f"   Error: {create_response.text}")
        else:
            print("✅ ExamSoft folder exists")
        
        # Check if Import folder exists
        import_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft/Import"
        import_response = requests.get(import_url, headers=headers)
        
        if import_response.status_code == 404:
            # Create Import folder
            print("📁 Creating Import folder...")
            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft:/children"
            folder_data = {
                "name": "Import",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_url, headers=headers, json=folder_data)
            print(f"   Result: {create_response.status_code}")
            if create_response.status_code not in [200, 201]:
                print(f"   Error: {create_response.text}")
        else:
            print("✅ Import folder exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating folders: {str(e)}")
        return False

def upload_to_sharepoint_with_validation(access_token, file_content, filename):
    """Upload with full validation and debugging using the correct path structure"""
    
    print("🔧 Using UPDATED upload function with correct Exam Procedures path!")
    
    site_id = "charlestonlaw.sharepoint.com,ba0b6d09-2f32-4ccf-a24d-9a41e9be4a6a,ffe7f195-f2eb-4f68-af47-35a01fa9a2d7"
    
    print(f"\n🚀 Starting upload process...")
    print(f"📄 Filename: {filename}")
    print(f"📊 Content size: {len(file_content) if hasattr(file_content, '__len__') else 'unknown'}")
    print(f"🏷️ Content type: {type(file_content)}")
    
    # Skip site access test for now - just try direct upload with correct path
    print(f"\n📋 Uploading file with CORRECTED path structure...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }
    
    try:
        # Convert content to bytes if needed
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
            print(f"🔄 Converted string to bytes")
        
        # Build upload URL with the CORRECT path structure
        # The path needs to be: /Exam Procedures/ExamSoft/Import/filename
        encoded_filename = quote(filename)
        
        # Use the CORRECTED path structure that matches the SharePoint URL
        folder_path = "Exam Procedures/ExamSoft/Import"
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{encoded_filename}:/content"
        
        print(f"🔗 CORRECTED Upload URL: {upload_url}")
        print(f"📁 CORRECTED Folder path: {folder_path}")
        print(f"✅ This should match: https://charlestonlaw.sharepoint.com/sites/acad_affairs/Exam%20Procedures/ExamSoft/Import/")
        
        # Upload
        response = requests.put(upload_url, headers=headers, data=file_content)
        
        print(f"📤 Upload response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            file_size = response_data.get('size', 0)
            
            print(f"✅ Upload successful!")
            print(f"🔗 File URL: {file_url}")
            
            return True, {
                'url': file_url,
                'size': file_size,
                'created': response_data.get('createdDateTime', 'N/A'),
                'message': 'Successfully uploaded to Exam Procedures / ExamSoft / Import'
            }
        else:
            error_msg = f"Upload failed: {response.status_code}"
            try:
                error_data = response.json()
                error_details = error_data.get('error', {})
                error_msg += f" - {error_details.get('message', 'Unknown error')}"
                print(f"❌ Error details: {error_data}")
                
                # If it's a path issue, maybe the site structure is different
                if "does not exist" in error_details.get('message', '').lower() or response.status_code == 400:
                    print(f"\n🔄 Path might be wrong, trying alternative approaches...")
                    
                    # Try without "Exam Procedures" folder - maybe files go directly in site root
                    alt_folder_path = "ExamSoft/Import"
                    alt_upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{alt_folder_path}/{encoded_filename}:/content"
                    print(f"� Trying alternative path: {alt_upload_url}")
                    
                    alt_response = requests.put(alt_upload_url, headers=headers, data=file_content)
                    print(f"📤 Alternative upload response: {alt_response.status_code}")
                    
                    if alt_response.status_code in [200, 201]:
                        response_data = alt_response.json()
                        file_url = response_data.get('webUrl', 'URL not available')
                        file_size = response_data.get('size', 0)
                        print(f"✅ Alternative path worked!")
                        return True, {
                            'url': file_url,
                            'size': file_size,
                            'created': response_data.get('createdDateTime', 'N/A'),
                            'message': 'Successfully uploaded to ExamSoft / Import'
                        }
                    else:
                        print(f"❌ Alternative path also failed: {alt_response.text}")
                
            except:
                error_msg += f" - {response.text}"
                print(f"❌ Error text: {response.text}")
            
            return False, error_msg
            
    except Exception as e:
        print(f"❌ Exception during upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Upload error: {str(e)}"

def create_folder_structure_with_space(access_token, site_id):
    """Create the folder structure: /Exam Procedures/ExamSoft/Import/"""
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # First check if "Exam Procedures" folder exists in root
        exam_procedures_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/Exam Procedures"
        exam_procedures_response = requests.get(exam_procedures_url, headers=headers)
        
        if exam_procedures_response.status_code == 404:
            print("📁 Creating 'Exam Procedures' folder...")
            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
            folder_data = {
                "name": "Exam Procedures",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_url, headers=headers, json=folder_data)
            print(f"   Result: {create_response.status_code}")
            if create_response.status_code not in [200, 201]:
                print(f"   Error: {create_response.text}")
                return False
        else:
            print("✅ 'Exam Procedures' folder exists")
        
        # Then check if ExamSoft folder exists inside Exam Procedures
        examsoft_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/Exam Procedures/ExamSoft"
        examsoft_response = requests.get(examsoft_url, headers=headers)
        
        if examsoft_response.status_code == 404:
            print("📁 Creating 'ExamSoft' folder inside 'Exam Procedures'...")
            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/Exam Procedures:/children"
            folder_data = {
                "name": "ExamSoft",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_url, headers=headers, json=folder_data)
            print(f"   Result: {create_response.status_code}")
            if create_response.status_code not in [200, 201]:
                print(f"   Error: {create_response.text}")
                return False
        else:
            print("✅ 'ExamSoft' folder exists")
        
        # Finally check if Import folder exists inside ExamSoft
        import_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/Exam Procedures/ExamSoft/Import"
        import_response = requests.get(import_url, headers=headers)
        
        if import_response.status_code == 404:
            print("📁 Creating 'Import' folder inside 'ExamSoft'...")
            create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/Exam Procedures/ExamSoft:/children"
            folder_data = {
                "name": "Import",
                "folder": {},
                "@microsoft.graph.conflictBehavior": "replace"
            }
            create_response = requests.post(create_url, headers=headers, json=folder_data)
            print(f"   Result: {create_response.status_code}")
            if create_response.status_code not in [200, 201]:
                print(f"   Error: {create_response.text}")
                return False
        else:
            print("✅ 'Import' folder exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating folder structure: {str(e)}")
        return False
