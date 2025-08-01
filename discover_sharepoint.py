#!/usr/bin/env python3
"""
SharePoint Folder Discovery Tool
This will help us discover the actual folder structure and test uploads step by step
"""

import requests
import json
from urllib.parse import quote

def discover_sharepoint_structure():
    """Discover the actual SharePoint folder structure"""
    
    # You'll need to paste your access token here temporarily
    access_token = input("Please paste your access token from the Streamlit app: ").strip()
    
    if not access_token:
        print("❌ No access token provided")
        return
    
    site_id = "b!CW0LujIvz0yiTZpB6b5KapXx5__r8mhPr0c1oB-potdx8f8gTKjDS4IT4o-6IPip"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    print("🔍 Discovering SharePoint folder structure...")
    
    # Step 1: List root folders
    try:
        root_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
        response = requests.get(root_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            folders = []
            files = []
            
            for item in data.get('value', []):
                if item.get('folder'):
                    folders.append({
                        'name': item['name'],
                        'id': item['id'],
                        'webUrl': item.get('webUrl', 'N/A')
                    })
                else:
                    files.append(item['name'])
            
            print(f"📁 Root folders found: {len(folders)}")
            for i, folder in enumerate(folders):
                print(f"   {i+1}. {folder['name']}")
            
            if files:
                print(f"📄 Root files: {files[:5]}")  # Show first 5 files
            
            # Step 2: Look for "Exam Procedures" folder
            exam_procedures_folder = None
            for folder in folders:
                if 'exam' in folder['name'].lower() and 'procedures' in folder['name'].lower():
                    exam_procedures_folder = folder
                    break
            
            if exam_procedures_folder:
                print(f"\n✅ Found 'Exam Procedures' folder: {exam_procedures_folder['name']}")
                
                # Step 3: Look inside Exam Procedures
                exam_proc_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{exam_procedures_folder['id']}/children"
                exam_proc_response = requests.get(exam_proc_url, headers=headers)
                
                if exam_proc_response.status_code == 200:
                    exam_proc_data = exam_proc_response.json()
                    exam_proc_folders = [item['name'] for item in exam_proc_data.get('value', []) if item.get('folder')]
                    print(f"📁 Inside 'Exam Procedures': {exam_proc_folders}")
                    
                    # Look for ExamSoft folder
                    examsoft_folder = None
                    for item in exam_proc_data.get('value', []):
                        if item.get('folder') and 'examsoft' in item['name'].lower():
                            examsoft_folder = item
                            break
                    
                    if examsoft_folder:
                        print(f"✅ Found ExamSoft folder: {examsoft_folder['name']}")
                        
                        # Look inside ExamSoft
                        examsoft_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{examsoft_folder['id']}/children"
                        examsoft_response = requests.get(examsoft_url, headers=headers)
                        
                        if examsoft_response.status_code == 200:
                            examsoft_data = examsoft_response.json()
                            examsoft_contents = [item['name'] for item in examsoft_data.get('value', [])]
                            print(f"📁 Inside ExamSoft: {examsoft_contents}")
                            
                            # Test upload to this location
                            return test_upload_to_examsoft(access_token, site_id, examsoft_folder['id'])
                        else:
                            print(f"❌ Cannot access ExamSoft folder: {examsoft_response.status_code}")
                    else:
                        print("❌ ExamSoft folder not found inside Exam Procedures")
                        
                        # Try to create ExamSoft folder
                        return create_examsoft_structure(access_token, site_id, exam_procedures_folder['id'])
                else:
                    print(f"❌ Cannot access Exam Procedures contents: {exam_proc_response.status_code}")
            else:
                print("❌ 'Exam Procedures' folder not found in root")
                print("Available folders:", [f['name'] for f in folders])
                
                # Try to create the folder structure
                return create_full_structure(access_token, site_id)
        else:
            print(f"❌ Cannot access root folders: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_upload_to_examsoft(access_token, site_id, examsoft_folder_id):
    """Test upload directly to ExamSoft folder using folder ID"""
    
    print(f"\n🧪 Testing upload using folder ID method...")
    
    # Create test content
    test_content = "This is a test file for SharePoint upload validation."
    file_content = test_content.encode('utf-8')
    filename = "test_upload.txt"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream'
    }
    
    # Method 1: Upload using folder ID
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{examsoft_folder_id}:/{filename}:/content"
    
    print(f"🔗 Upload URL: {upload_url}")
    
    response = requests.put(upload_url, headers=headers, data=file_content)
    print(f"📤 Upload response: {response.status_code}")
    
    if response.status_code in [200, 201]:
        response_data = response.json()
        file_url = response_data.get('webUrl', 'URL not available')
        print(f"✅ SUCCESS! File uploaded: {file_url}")
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw error: {response.text}")
        return False

def create_examsoft_structure(access_token, site_id, exam_procedures_folder_id):
    """Create ExamSoft/Import structure inside Exam Procedures"""
    
    print(f"\n📁 Creating ExamSoft folder structure...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create ExamSoft folder
    create_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{exam_procedures_folder_id}/children"
    folder_data = {
        "name": "ExamSoft",
        "folder": {},
        "@microsoft.graph.conflictBehavior": "replace"
    }
    
    response = requests.post(create_url, headers=headers, json=folder_data)
    print(f"ExamSoft creation: {response.status_code}")
    
    if response.status_code in [200, 201]:
        examsoft_data = response.json()
        examsoft_id = examsoft_data['id']
        
        # Create Import folder inside ExamSoft
        import_data = {
            "name": "Import",
            "folder": {},
            "@microsoft.graph.conflictBehavior": "replace"
        }
        
        import_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{examsoft_id}/children"
        import_response = requests.post(import_url, headers=headers, json=import_data)
        print(f"Import folder creation: {import_response.status_code}")
        
        if import_response.status_code in [200, 201]:
            import_folder_data = import_response.json()
            print(f"✅ Created full structure: Exam Procedures/ExamSoft/Import")
            return test_upload_to_examsoft(access_token, site_id, import_folder_data['id'])
        else:
            print(f"❌ Failed to create Import folder: {import_response.text}")
    else:
        print(f"❌ Failed to create ExamSoft folder: {response.text}")
    
    return False

def create_full_structure(access_token, site_id):
    """Create the full Exam Procedures/ExamSoft/Import structure"""
    
    print(f"\n📁 Creating full folder structure from root...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Create Exam Procedures folder in root
    root_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children"
    exam_proc_data = {
        "name": "Exam Procedures",
        "folder": {},
        "@microsoft.graph.conflictBehavior": "replace"
    }
    
    response = requests.post(root_url, headers=headers, json=exam_proc_data)
    print(f"Exam Procedures creation: {response.status_code}")
    
    if response.status_code in [200, 201]:
        exam_proc_folder = response.json()
        return create_examsoft_structure(access_token, site_id, exam_proc_folder['id'])
    else:
        print(f"❌ Failed to create Exam Procedures folder: {response.text}")
        return False

if __name__ == "__main__":
    discover_sharepoint_structure()
