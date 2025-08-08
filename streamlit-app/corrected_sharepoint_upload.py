"""
Corrected SharePoint upload functions that target the IT site correctly
"""

def upload_to_sharepoint_corrected(access_token, file_content, filename):
    """Upload to correct SharePoint path: IT/Shared Documents/ExamSoft/File-converter/Import with robust error handling"""
    try:
        import requests
        from urllib.parse import quote
        import re
        
        print("🔧 Using CORRECTED upload function with IT site targeting!")
        print("🎯 Targeting IT SharePoint site for upload...")
        
        # Step 1: Clean and validate filename
        clean_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        clean_filename = re.sub(r'\s+', '_', clean_filename)  # Replace spaces with underscores
        clean_filename = clean_filename[:255]  # Limit length
        
        if clean_filename != filename:
            print(f"🔧 Cleaned filename: '{filename}' → '{clean_filename}'")
        
        # Step 2: Validate and prepare file content
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
            print(f"🔄 Converted string to bytes")
        
        if not isinstance(file_content, bytes):
            print(f"❌ Invalid content type: {type(file_content)}")
            return False, f"Invalid content type: {type(file_content)}"
        
        content_size = len(file_content)
        print(f"📊 Content size: {content_size:,} bytes")
        
        # Check for reasonable file size
        if content_size > 100 * 1024 * 1024:  # 100MB limit
            return False, f"File too large: {content_size:,} bytes (limit: 100MB)"
        
        if content_size == 0:
            return False, "Empty file content"
        
        # Step 3: Use different upload methods based on file size
        if content_size > 4 * 1024 * 1024:  # > 4MB, use session upload
            print("📤 Large file detected, using upload session...")
            return upload_large_file_with_session(access_token, file_content, clean_filename)
        else:
            print("📤 Small file, using direct upload...")
            return upload_small_file_direct(access_token, file_content, clean_filename)
            
    except Exception as e:
        print(f"❌ Exception in upload preparation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Upload preparation error: {str(e)}"

def upload_small_file_direct(access_token, file_content, filename):
    """Direct upload for small files to IT site with correct path"""
    import requests
    from urllib.parse import quote
    
    encoded_filename = quote(filename)
    
    print(f"🔍 Looking for IT SharePoint site...")
    
    # Step 1: Find the IT site
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Try to get IT site directly by URL
        it_url_response = requests.get(
            "https://graph.microsoft.com/v1.0/sites/charlestonlaw.sharepoint.com:/sites/IT",
            headers=headers
        )
        if it_url_response.status_code == 200:
            it_site = it_url_response.json()
            site_id = it_site['id']
            print(f"✅ Found IT site via direct URL: {it_site.get('webUrl')}")
        else:
            print(f"❌ Cannot access IT site: {it_url_response.status_code}")
            return False, "Cannot access IT SharePoint site"
            
    except Exception as e:
        print(f"❌ Error finding IT site: {e}")
        return False, f"Error finding IT site: {e}"
    
    # Step 2: Target the EXACT correct IT SharePoint folder path - FOUND BY EXPLORATION!
    print(f"🎯 Targeting CONFIRMED IT SharePoint folder: ExamSoft/File-converter/Import")
    
    # These are the ACTUAL paths found by exploration - ExamSoft is in root, NOT Documents!
    target_paths = [
        'ExamSoft/File-converter/Import',      # CONFIRMED target Import folder
        'ExamSoft%2FFile-converter%2FImport',  # URL encoded version
        'ExamSoft/File-converter/Import/',     # With trailing slash
        'ExamSoft/File-converter',             # Parent File-converter folder fallback
        'ExamSoft',                            # ExamSoft folder fallback
    ]
    
    print(f"📋 Will try these CONFIRMED paths in order:")
    for i, path in enumerate(target_paths, 1):
        print(f"   {i}. {path}")
    
    # Verify the target Import folder exists (we know it does from exploration)
    try:
        target_check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/ExamSoft/File-converter/Import"
        check_response = requests.get(target_check_url, headers=headers)
        if check_response.status_code == 200:
            print(f"✅ CONFIRMED target Import folder exists: ExamSoft/File-converter/Import")
        else:
            print(f"⚠️  Target Import folder check returned {check_response.status_code}, will try upload anyway")
    except Exception as e:
        print(f"ℹ️  Could not verify target Import folder (will try upload anyway): {e}")
    
    print(f"🎯 Using IT site ID: {site_id}")
    
    for target_path in target_paths:
        print(f"\n📂 Trying path: {target_path}")
        
        # Build the correct URL based on whether path is empty or not
        if target_path:
            # URL encode the path for special characters
            encoded_path = quote(target_path, safe='/')
            check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}"
            upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}/{encoded_filename}:/content"
        else:
            # Root folder
            check_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root"
            upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children/{encoded_filename}/content"
        
        try:
            # Check if the path exists (or try root if no path)
            if target_path:
                check_response = requests.get(check_url, headers=headers)
                print(f"   Path check: {check_response.status_code}")
                path_exists = check_response.status_code == 200
            else:
                # Root always exists
                path_exists = True
                print(f"   Using root folder")
            
            if path_exists:
                print(f"   ✅ Path accessible!")
                print(f"   📤 Upload URL: {upload_url}")
                
                upload_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/octet-stream'
                }
                
                # For root folder, use different upload method
                if not target_path:
                    # Create file in root using Graph API
                    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_filename}:/content"
                
                response = requests.put(upload_url, headers=upload_headers, data=file_content, timeout=60)
                print(f"   📤 Upload response: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    file_url = response_data.get('webUrl', 'URL not available')
                    
                    print(f"✅ SUCCESS! File uploaded to IT site")
                    print(f"🔗 File URL: {file_url}")
                    
                    return True, {
                        'url': file_url,
                        'site': 'IT',
                        'path': target_path or 'root',
                        'size': response_data.get('size', 0),
                        'message': f'Successfully uploaded to IT site at {target_path or "root"}'
                    }
                else:
                    print(f"   ❌ Upload failed: {response.status_code}")
                    if response.text:
                        print(f"   Response: {response.text[:200]}")
                    
            else:
                print(f"   📂 Path not found, trying next...")
                
        except Exception as e:
            print(f"   ❌ Error with path {target_path}: {e}")
    
    print(f"❌ All upload attempts failed")
    return False, "Could not upload to any path in IT site"

def upload_large_file_with_session(access_token, file_content, filename):
    """Upload large files using upload session to IT site"""
    try:
        import requests
        from urllib.parse import quote
    except ImportError:
        print("❌ Required modules not available for large file upload")
        return False, "Required modules not available"
    
    print(f"📤 Initiating upload session for large file...")
    
    # First find the IT site (same as in small file upload)
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Try to get IT site directly by URL
        it_url_response = requests.get(
            "https://graph.microsoft.com/v1.0/sites/charlestonlaw.sharepoint.com:/sites/IT",
            headers=headers
        )
        if it_url_response.status_code == 200:
            it_site = it_url_response.json()
            site_id = it_site['id']
            print(f"✅ Found IT site via direct URL: {it_site.get('webUrl')}")
        else:
            print(f"❌ Cannot access IT site: {it_url_response.status_code}")
            return False, "Cannot access IT SharePoint site for large file upload"
            
    except Exception as e:
        print(f"❌ Error finding IT site: {e}")
        return False, f"Error finding IT site: {e}"
    
    encoded_filename = quote(filename)
    folder_path = "ExamSoft/File-converter/Import"
    
    # Create upload session
    session_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{encoded_filename}:/createUploadSession"
    
    session_headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    session_data = {
        "item": {
            "@microsoft.graph.conflictBehavior": "replace"
        }
    }
    
    try:
        session_response = requests.post(session_url, headers=session_headers, json=session_data)
        print(f"🔗 Session creation: {session_response.status_code}")
        
        if session_response.status_code in [200, 201]:
            session_info = session_response.json()
            upload_url = session_info['uploadUrl']
            
            # Upload in chunks
            chunk_size = 327680  # 320KB chunks (must be multiple of 327680)
            total_size = len(file_content)
            
            for start in range(0, total_size, chunk_size):
                end = min(start + chunk_size, total_size)
                chunk = file_content[start:end]
                
                chunk_headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {start}-{end-1}/{total_size}'
                }
                
                chunk_response = requests.put(upload_url, headers=chunk_headers, data=chunk)
                print(f"📦 Chunk {start//chunk_size + 1}: {chunk_response.status_code}")
                
                if chunk_response.status_code not in [202, 200, 201]:
                    print(f"❌ Chunk upload failed: {chunk_response.text}")
                    return False, f"Chunk upload failed: {chunk_response.status_code}"
            
            # Final response should contain file info
            if chunk_response.status_code in [200, 201]:
                response_data = chunk_response.json()
                return True, {
                    'url': response_data.get('webUrl', 'URL not available'),
                    'size': response_data.get('size', 0),
                    'created': response_data.get('createdDateTime', 'N/A'),
                    'message': 'Successfully uploaded large file'
                }
            else:
                return False, f"Upload session completed but final status unclear: {chunk_response.status_code}"
        else:
            print(f"❌ Session creation failed: {session_response.text}")
            return False, f"Could not create upload session: {session_response.status_code}"
            
    except Exception as e:
        print(f"❌ Upload session error: {str(e)}")
        return False, f"Upload session error: {str(e)}"
