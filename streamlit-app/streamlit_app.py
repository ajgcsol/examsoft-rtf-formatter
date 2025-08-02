import streamlit as st
import sys
import traceback

# Configure page
st.set_page_config(
    page_title="ExamSoft RTF Formatter - Charleston School of Law",
    page_icon="📝",
    layout="wide"
)

def render_text_paste_method():
    """Render the text paste method UI"""
    from safe_formatter import (
        clean_text_encoding, parse_questions_from_text, generate_filename,
        create_rtf_content, generate_instructions_docx, 
        generate_docx_with_questions, convert_docx_to_rtf_via_api,
        get_converter_endpoint, is_using_azure, upload_to_sharepoint_corrected
    )
    
    # Try to import SharePoint functionality
    try:
        from persistent_auth import initialize_persistent_auth, render_persistent_auth_ui, render_auth_status, sign_out_persistent
        SHAREPOINT_AVAILABLE = True
    except (ImportError, AttributeError):
        SHAREPOINT_AVAILABLE = False

    # File naming inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        course_input = st.text_input("Course", placeholder="e.g., CONST", key="course_input")
    with col2:
        section_input = st.text_input("Section", placeholder="e.g., 001", key="section_input")
    with col3:
        professor_input = st.text_input("Professor Last Name", placeholder="e.g., Smith", key="professor_input")

    st.subheader("Instructions (Optional)")
    instructions_input = st.text_area("Paste Instructions", height=150, key="instructions_input",
                                     help="Optional: Paste or type the exam instructions. Leave blank if not needed.")

    st.subheader("Exam Questions (Required)")
    questions_input = st.text_area("Paste Exam Questions", height=400, key="questions_input",
                                 help="Paste all exam questions as plain text, including numbering and answer choices.")

    st.subheader("Answer Key")
    answer_key_input = st.text_area("Paste Answer Key", height=150, key="answer_key_input",
                                   help="Paste a single column of answers (A, B, C, D, etc.) from Excel or CSV. One per line.")

    st.subheader("Answer Key Method")
    answer_method = st.radio(
        "How would you like to handle answer keys?",
        ("Asterisk Method (mark correct answers with * in questions)", 
         "Answer Key Section (add separate answer list at end)"),
        key="answer_method",
        help="ExamSoft supports both methods."
    )
    use_asterisk_method = answer_method.startswith("Asterisk")

    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None

    # Process button
    if st.button("Process Data", key="process_data_btn"):
        if not questions_input.strip():
            st.error("Exam questions are required. Please paste your questions above.")
        else:
            # Parse answer key with header detection
            from safe_formatter import parse_answer_key_with_header_detection
            answer_key = parse_answer_key_with_header_detection(answer_key_input)
            st.write(f"Answer key loaded: {len(answer_key)} answers")

            # Generate filenames
            instructions_filename = generate_filename(course_input, section_input, professor_input, "ins", "docx")
            exam_filename = generate_filename(course_input, section_input, professor_input, "exm", "rtf")

            # Process content
            instructions_text = clean_text_encoding(instructions_input.strip()) if instructions_input.strip() else ""
            questions_text = questions_input.strip()

            # Parse questions
            questions_list = parse_questions_from_text(questions_text, answer_key, use_asterisk_method)

            if questions_list:
                # Count questions
                mc_count = sum(1 for q in questions_list if not q.startswith("Type: E"))
                essay_count = sum(1 for q in questions_list if q.startswith("Type: E"))

                # Generate files
                instructions_docx = None
                if instructions_text:
                    instructions_docx = generate_instructions_docx(instructions_text)

                exam_rtf_content = create_rtf_content(
                    questions_list, 
                    answer_key if not use_asterisk_method else None, 
                    not use_asterisk_method
                )

                # Try LibreOffice conversion
                exam_rtf_bytes = None
                try:
                    import tempfile
                    import os
                    with tempfile.TemporaryDirectory() as tmpdir:
                        docx_path = os.path.join(tmpdir, "ExamSoft_Export.docx")
                        rtf_path = os.path.join(tmpdir, "ExamSoft_Export.rtf")
                        generate_docx_with_questions(questions_list, '', docx_path)
                        
                        api_endpoint = get_converter_endpoint()
                        convert_docx_to_rtf_via_api(docx_path, rtf_path, api_url=api_endpoint)
                        with open(rtf_path, "rb") as f:
                            exam_rtf_bytes = f.read()
                        
                        if is_using_azure():
                            st.success("✅ RTF generated using Azure LibreOffice API")
                        else:
                            st.success("✅ RTF generated using local LibreOffice Docker API")
                except Exception as e:
                    st.error(f"❌ LibreOffice API conversion failed: {e}")
                    st.info("🔄 Using basic RTF conversion as fallback.")

                # Store results
                st.session_state.processed_data = {
                    'instructions_text': instructions_text,
                    'instructions_docx': instructions_docx,
                    'instructions_filename': instructions_filename,
                    'questions_list': questions_list,
                    'exam_rtf_content': exam_rtf_content,
                    'exam_rtf_bytes': exam_rtf_bytes,
                    'exam_filename': exam_filename,
                    'mc_count': mc_count,
                    'essay_count': essay_count,
                    'answer_key': answer_key,
                    'use_asterisk_method': use_asterisk_method
                }

                st.success(f"Processed {len(questions_list)} questions successfully!")
                st.info(f"Found {mc_count} multiple choice questions and {essay_count} essay questions")
            else:
                st.error("No questions were found or formatted")

    # Display results
    if st.session_state.processed_data:
        render_results(SHAREPOINT_AVAILABLE, method_prefix="paste")

def render_file_upload_method():
    """Render the file upload method UI"""
    from safe_formatter import (
        clean_text_encoding, parse_questions_from_text, generate_filename,
        create_rtf_content, generate_instructions_docx, 
        generate_docx_with_questions, convert_docx_to_rtf_via_api,
        get_converter_endpoint, is_using_azure, upload_to_sharepoint_corrected
    )
    
    # Try to import SharePoint functionality
    try:
        from persistent_auth import initialize_persistent_auth, render_persistent_auth_ui, render_auth_status, sign_out_persistent
        SHAREPOINT_AVAILABLE = True
    except (ImportError, AttributeError):
        SHAREPOINT_AVAILABLE = False

    # File naming inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        course_input = st.text_input("Course", placeholder="e.g., CONST", key="file_course_input")
    with col2:
        section_input = st.text_input("Section", placeholder="e.g., 001", key="file_section_input")
    with col3:
        professor_input = st.text_input("Professor Last Name", placeholder="e.g., Smith", key="file_professor_input")

    st.subheader("Upload Files")
    
    # Instructions file upload
    st.write("**Instructions File (Optional)**")
    instructions_file = st.file_uploader(
        "Upload instructions file", 
        type=['docx', 'rtf', 'txt'],
        key="instructions_file_upload",
        help="Upload a Word document, RTF, or text file containing exam instructions"
    )
    
    # Questions file upload
    st.write("**Questions File (Required)**")
    questions_file = st.file_uploader(
        "Upload questions file", 
        type=['docx', 'rtf', 'txt', 'csv', 'xlsx'],
        key="questions_file_upload",
        help="Upload a file containing exam questions and answer choices"
    )
    
    # Answer key file upload
    st.write("**Answer Key File (Optional)**")
    answer_key_file = st.file_uploader(
        "Upload answer key file", 
        type=['txt', 'csv', 'xlsx'],
        key="answer_key_file_upload",
        help="Upload a file containing the answer key. For Excel/CSV: answers should be in the first column. For TXT: one answer per line (A, B, C, D, etc.)"
    )

    st.subheader("Answer Key Method")
    answer_method = st.radio(
        "How would you like to handle answer keys?",
        ("Asterisk Method (mark correct answers with * in questions)", 
         "Answer Key Section (add separate answer list at end)"),
        key="file_answer_method",
        help="ExamSoft supports both methods."
    )
    use_asterisk_method = answer_method.startswith("Asterisk")

    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None

    # Process button
    if st.button("Process Files", key="process_files_btn"):
        if not questions_file:
            st.error("Questions file is required. Please upload your questions file above.")
        else:
            try:
                # Process instructions
                instructions_text = ""
                if instructions_file:
                    instructions_text = extract_text_from_file(instructions_file)
                
                # Process questions file and auto-detect instructions
                full_text = extract_text_from_file(questions_file)
                
                # Try to automatically separate instructions and questions
                parsed_instructions, parsed_questions = parse_instructions_and_questions(full_text)
                
                # Show parsing preview
                st.subheader("🤖 Automatic Parsing Results")
                st.write("The system attempted to separate instructions from questions:")
                
                final_instructions, final_questions = preview_parsed_content(parsed_instructions, parsed_questions)
                
                # Allow manual override
                st.subheader("✏️ Manual Adjustments (Optional)")
                method_prefix = "file"  # Define method_prefix for this function
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.checkbox("Override instructions", key=f"override_instructions_{method_prefix}"):
                        final_instructions = st.text_area(
                            "Edit Instructions",
                            value=final_instructions,
                            height=200,
                            key=f"manual_instructions_{method_prefix}"
                        )
                
                with col2:
                    if st.checkbox("Override questions", key=f"override_questions_{method_prefix}"):
                        final_questions = st.text_area(
                            "Edit Questions", 
                            value=final_questions,
                            height=200,
                            key=f"manual_questions_{method_prefix}"
                        )
                
                # Use parsed content
                questions_text = final_questions
                
                # Override instructions from separate file if both exist
                if instructions_text and final_instructions:
                    st.info("ℹ️ Both separate instructions file and parsed instructions found. Using separate file.")
                elif final_instructions and not instructions_text:
                    instructions_text = final_instructions
                    st.success("✅ Using auto-detected instructions from questions file!")
                
                # Process answer key
                answer_key = []
                if answer_key_file:
                    st.write(f"📄 Processing answer key file: {answer_key_file.name} ({answer_key_file.type})")
                    answer_key = extract_answer_key_from_file(answer_key_file)
                
                if answer_key:
                    st.success(f"✅ Answer key loaded: {len(answer_key)} answers")
                    st.write("📝 First few answers:", answer_key[:5])
                else:
                    st.info("ℹ️ No answer key provided - answers will need to be marked manually in questions.")

                # Generate filenames
                instructions_filename = generate_filename(course_input, section_input, professor_input, "ins", "docx")
                exam_filename = generate_filename(course_input, section_input, professor_input, "exm", "rtf")

                # Parse questions
                questions_list = parse_questions_from_text(questions_text, answer_key, use_asterisk_method)

                if questions_list:
                    # Count questions
                    mc_count = sum(1 for q in questions_list if not q.startswith("Type: E"))
                    essay_count = sum(1 for q in questions_list if q.startswith("Type: E"))

                    # Generate files
                    instructions_docx = None
                    if instructions_text:
                        instructions_docx = generate_instructions_docx(instructions_text)

                    exam_rtf_content = create_rtf_content(
                        questions_list, 
                        answer_key if not use_asterisk_method else None, 
                        not use_asterisk_method
                    )

                    # Try LibreOffice conversion
                    exam_rtf_bytes = None
                    try:
                        import tempfile
                        import os
                        with tempfile.TemporaryDirectory() as tmpdir:
                            docx_path = os.path.join(tmpdir, "ExamSoft_Export.docx")
                            rtf_path = os.path.join(tmpdir, "ExamSoft_Export.rtf")
                            generate_docx_with_questions(questions_list, '', docx_path)
                            
                            api_endpoint = get_converter_endpoint()
                            convert_docx_to_rtf_via_api(docx_path, rtf_path, api_url=api_endpoint)
                            with open(rtf_path, "rb") as f:
                                exam_rtf_bytes = f.read()
                            
                            if is_using_azure():
                                st.success("✅ RTF generated using Azure LibreOffice API")
                            else:
                                st.success("✅ RTF generated using local LibreOffice Docker API")
                    except Exception as e:
                        st.error(f"❌ LibreOffice API conversion failed: {e}")
                        st.info("🔄 Using basic RTF conversion as fallback.")

                    # Store results
                    st.session_state.processed_data = {
                        'instructions_text': instructions_text,
                        'instructions_docx': instructions_docx,
                        'instructions_filename': instructions_filename,
                        'questions_list': questions_list,
                        'exam_rtf_content': exam_rtf_content,
                        'exam_rtf_bytes': exam_rtf_bytes,
                        'exam_filename': exam_filename,
                        'mc_count': mc_count,
                        'essay_count': essay_count,
                        'answer_key': answer_key,
                        'use_asterisk_method': use_asterisk_method
                    }

                    st.success(f"Processed {len(questions_list)} questions successfully!")
                    st.info(f"Found {mc_count} multiple choice questions and {essay_count} essay questions")
                else:
                    st.error("No questions were found or formatted")
                    
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
                st.error("Please check your file formats and try again.")

    # Display results
    if st.session_state.processed_data:
        render_results(SHAREPOINT_AVAILABLE, method_prefix="file")

def extract_text_from_file(uploaded_file):
    """Extract text content from uploaded file"""
    import io
    
    file_type = uploaded_file.type
    content = uploaded_file.read()
    
    if file_type == "text/plain":
        return content.decode('utf-8')
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # DOCX file
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except:
            st.error("Failed to read DOCX file. Please ensure it's a valid Word document.")
            return ""
    elif file_type == "application/rtf" or uploaded_file.name.endswith('.rtf'):
        # RTF file - basic text extraction
        try:
            from striprtf.striprtf import rtf_to_text
            return rtf_to_text(content.decode('utf-8'))
        except:
            # Fallback to basic parsing
            text = content.decode('utf-8', errors='ignore')
            # Remove RTF control codes (basic cleanup)
            import re
            text = re.sub(r'\\[a-z]+\d*', '', text)
            text = re.sub(r'[{}]', '', text)
            return text.strip()
    elif file_type == "text/csv":
        # CSV file
        try:
            import pandas as pd
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            return '\n'.join([' '.join(str(val) for val in row if pd.notna(val)) for _, row in df.iterrows()])
        except:
            st.error("Failed to read CSV file. Please ensure it's properly formatted.")
            return ""
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        # XLSX file
        try:
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content))
            return '\n'.join([' '.join(str(val) for val in row if pd.notna(val)) for _, row in df.iterrows()])
        except ImportError:
            st.error("❌ Pandas library not available for Excel files. Please convert to CSV or TXT format.")
            return ""
        except Exception as e:
            st.error(f"❌ Failed to read Excel file: {str(e)}")
            st.info("💡 Try converting your Excel file to CSV or TXT format.")
            return ""
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""

def parse_instructions_and_questions(text):
    """
    Intelligently parse a document to separate instructions from questions
    Returns (instructions_text, questions_text)
    """
    import re
    
    lines = text.split('\n')
    instructions_lines = []
    questions_lines = []
    
    # Common patterns that indicate the start of questions
    question_start_patterns = [
        r'^\s*1[\.\)]\s+',  # "1. " or "1) "
        r'^\s*Question\s*1',  # "Question 1"
        r'^\s*QUESTION\s*1',  # "QUESTION 1"
        r'^\s*Q\s*1[\.\)]\s+',  # "Q 1. " or "Q 1) "
    ]
    
    # Common instruction section indicators
    instruction_indicators = [
        'instructions', 'directions', 'exam instructions', 'test instructions',
        'general instructions', 'please read', 'important', 'time limit',
        'multiple choice', 'essay questions', 'answer sheet', 'bubble sheet'
    ]
    
    # Find where questions likely start
    question_start_line = None
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Check for numbered question patterns
        for pattern in question_start_patterns:
            if re.match(pattern, stripped_line, re.IGNORECASE):
                question_start_line = i
                break
        
        if question_start_line is not None:
            break
    
    # If we found a clear question start, split there
    if question_start_line is not None:
        instructions_lines = lines[:question_start_line]
        questions_lines = lines[question_start_line:]
        
        # Clean up instructions - remove empty lines at the end
        while instructions_lines and not instructions_lines[-1].strip():
            instructions_lines.pop()
        
        instructions_text = '\n'.join(instructions_lines).strip()
        questions_text = '\n'.join(questions_lines).strip()
        
        return instructions_text, questions_text
    
    # Fallback: Look for instruction keywords in the first part of the document
    # Assume instructions are in the first 30% of the document
    split_point = len(lines) // 3
    first_third = '\n'.join(lines[:split_point]).lower()
    
    # Count instruction indicators in first third
    instruction_score = sum(1 for indicator in instruction_indicators if indicator in first_third)
    
    # If we found instruction indicators, assume first third is instructions
    if instruction_score >= 2:  # At least 2 instruction keywords
        # Look for a better split point near the end of first third
        for i in range(split_point - 5, min(split_point + 10, len(lines))):
            if i < len(lines) and re.match(question_start_patterns[0], lines[i].strip()):
                split_point = i
                break
        
        instructions_text = '\n'.join(lines[:split_point]).strip()
        questions_text = '\n'.join(lines[split_point:]).strip()
        
        return instructions_text, questions_text
    
    # Final fallback: No clear separation found
    return "", text

def preview_parsed_content(instructions_text, questions_text):
    """Show a preview of how the content was parsed"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Detected Instructions")
        if instructions_text:
            preview_text = instructions_text[:300] + "..." if len(instructions_text) > 300 else instructions_text
            st.text_area("Instructions Preview", value=preview_text, height=150, disabled=True)
            st.caption(f"Length: {len(instructions_text)} characters")
        else:
            st.info("No instructions detected")
    
    with col2:
        st.subheader("❓ Detected Questions")
        if questions_text:
            preview_text = questions_text[:300] + "..." if len(questions_text) > 300 else questions_text
            st.text_area("Questions Preview", value=preview_text, height=150, disabled=True)
            st.caption(f"Length: {len(questions_text)} characters")
        else:
            st.warning("No questions detected")
    
    return instructions_text, questions_text

def extract_answer_key_from_file(uploaded_file):
    """Extract answer key from uploaded file"""
    import io
    
    file_type = uploaded_file.type
    content = uploaded_file.read()
    
    if file_type == "text/plain":
        text = content.decode('utf-8')
        return [line.strip() for line in text.splitlines() if line.strip()]
    elif file_type == "text/csv":
        try:
            import pandas as pd
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            # Take first column as answer key
            return [str(val).strip() for val in df.iloc[:, 0] if pd.notna(val)]
        except:
            st.error("Failed to read CSV answer key file.")
            return []
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        try:
            import pandas as pd
            # Read Excel with additional parameters to handle edge cases
            df = pd.read_excel(
                io.BytesIO(content), 
                header=None,  # Don't assume first row is header
                keep_default_na=False,  # Don't convert strings like 'NA' to NaN
                na_values=[''],  # Only treat empty strings as NaN
            )
            
            # Process first column as answer key
            first_column = df.iloc[:, 0]
            
            # Extract answers, handling various edge cases
            raw_answers = []
            for val in first_column:
                if pd.notna(val):  # Not NaN/None
                    str_val = str(val).strip()
                    if str_val:  # Not empty string
                        raw_answers.append(str_val)
            
            st.success(f"✅ Found {len(raw_answers)} answers in Excel file")
            
            # Add validation and guidance
            if len(raw_answers) < 10:
                st.warning(f"⚠️ Only {len(raw_answers)} answers found. This seems low for a typical exam.")
                with st.expander("💡 Excel File Tips"):
                    st.write("• Put one answer per row in the first column (A, B, C, D)")
                    st.write("• Don't include headers like 'Answer Key' or 'Question'")
                    st.write("• Make sure there are no empty rows between answers")
                    st.write("• Save as .xlsx format for best compatibility")
                st.info("• Make sure there are no empty rows between answers")
                st.info("• Save as .xlsx format")
            elif len(raw_answers) != 40:
                expected_from_instructions = 40  # You mentioned 40 questions
                st.info(f"📋 Found {len(raw_answers)} answers, expected around {expected_from_instructions}")
                if len(raw_answers) == 39:
                    st.warning("⚠️ Missing 1 answer! Check your Excel file for:")
                    st.info("• Empty rows that might contain an answer")
                    st.info("• Answers that got filtered as headers")
                    st.info("• The last row - sometimes it gets cut off")
            else:
                st.success(f"✅ Perfect! Found {len(raw_answers)} answers")
            
            return raw_answers
        except ImportError:
            st.error("❌ Pandas library not available for Excel files. Please convert to CSV or TXT format.")
            return []
        except Exception as e:
            st.error(f"❌ Failed to read Excel answer key file: {str(e)}")
            st.info("💡 Try converting your Excel file to CSV or TXT format, or check that the first column contains your answer key.")
            return []
    else:
        st.error(f"Unsupported answer key file type: {file_type}")
        return []

def upload_to_sharepoint_with_site(access_token, file_content, filename, site_id, path):
    """Upload file to a specific SharePoint site and path"""
    try:
        import requests
        from urllib.parse import quote
        
        encoded_filename = quote(filename)
        
        # Build upload URL
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{path}{encoded_filename}:/content"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        print(f"📤 Uploading to: {upload_url}")
        
        response = requests.put(upload_url, headers=headers, data=file_content, timeout=60)
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            file_url = response_data.get('webUrl', 'URL not available')
            
            return True, {
                'url': file_url,
                'size': response_data.get('size', 0),
                'created': response_data.get('createdDateTime', 'N/A')
            }
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"❌ Upload failed: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        print(f"❌ Upload exception: {str(e)}")
        return False, str(e)

def get_available_sharepoint_sites(access_token):
    """Get list of accessible SharePoint sites"""
    try:
        import requests
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get sites user has access to
        response = requests.get(
            'https://graph.microsoft.com/v1.0/sites?search=*',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            sites_data = response.json()
            sites = sites_data.get('value', [])
            
            # Filter out personal sites and keep only relevant ones
            filtered_sites = []
            for site in sites:
                if site.get('displayName') and 'personal' not in site.get('displayName', '').lower():
                    filtered_sites.append({
                        'id': site['id'],
                        'displayName': site['displayName'],
                        'webUrl': site['webUrl']
                    })
            
            print(f"📋 Found {len(filtered_sites)} accessible sites")
            return filtered_sites
        else:
            print(f"❌ Failed to get sites: {response.status_code} - {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"❌ Sites query exception: {str(e)}")
        return []

def get_folder_tree(access_token, site_id, folder_id=None, current_path=""):
    """Get hierarchical folder structure for SharePoint site"""
    try:
        import requests
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get folders - root or specific folder
        if folder_id:
            url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{folder_id}/children?$filter=folder ne null&$select=id,name,folder,webUrl'
        else:
            url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children?$filter=folder ne null&$select=id,name,folder,webUrl'
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            folders_data = response.json()
            folders = folders_data.get('value', [])
            
            formatted_folders = []
            for folder in folders:
                if folder.get('folder'):
                    folder_path = f"{current_path}/{folder['name']}" if current_path else folder['name']
                    formatted_folders.append({
                        'name': folder['name'],
                        'id': folder['id'],
                        'path': folder_path,
                        'webUrl': folder.get('webUrl', ''),
                        'hasChildren': folder.get('folder', {}).get('childCount', 0) > 0
                    })
            
            return formatted_folders
        else:
            print(f"❌ Failed to get folders: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Folder tree exception: {str(e)}")
        return []

def load_favorite_folders():
    """Load saved favorite folders from session state"""
    if 'favorite_folders' not in st.session_state:
        st.session_state.favorite_folders = [
            {
                'name': 'ExamSoft Import (Academic Affairs)',
                'site_id': 'charlestonlaw.sharepoint.com,ba0b6d09-2f32-4ccf-a24d-9a41e9be4a6a,ffe7f195-f2eb-4f68-af47-35a01fa9a2d7',
                'path': 'Exam Procedures/ExamSoft/Import',
                'is_default': True
            }
        ]
    return st.session_state.favorite_folders

def save_favorite_folder(name, site_id, path, is_default=False):
    """Save a folder to favorites"""
    favorites = load_favorite_folders()
    
    # Remove default flag from others if this is becoming default
    if is_default:
        for fav in favorites:
            fav['is_default'] = False
    
    # Add or update favorite
    existing = next((fav for fav in favorites if fav['path'] == path and fav['site_id'] == site_id), None)
    if existing:
        existing['name'] = name
        existing['is_default'] = is_default
    else:
        favorites.append({
            'name': name,
            'site_id': site_id,
            'path': path,
            'is_default': is_default
        })
    
    st.session_state.favorite_folders = favorites

def render_folder_browser(access_token, site_id, method_prefix):
    """Render an advanced folder browser with tree view and favorites"""
    st.write("📁 **Choose Upload Folder:**")
    
    # Load favorites
    favorites = load_favorite_folders()
    
    # Folder selection method
    folder_method = st.radio(
        "Folder Selection Method",
        ("⭐ Favorites", "🌳 Browse Folders", "✏️ Enter Path"),
        key=f"folder_method_{method_prefix}"
    )
    
    selected_folder_path = ""
    
    if folder_method == "⭐ Favorites":
        if favorites:
            favorite_options = [f"{'🏠 ' if fav['is_default'] else '📁 '}{fav['name']}" for fav in favorites]
            selected_fav_display = st.selectbox(
                "Select Favorite Folder",
                options=favorite_options,
                key=f"favorite_folder_{method_prefix}"
            )
            
            # Find selected favorite
            fav_index = favorite_options.index(selected_fav_display)
            selected_favorite = favorites[fav_index]
            selected_folder_path = selected_favorite['path']
            
            st.info(f"📍 **Path**: {selected_folder_path}")
            
            # Option to set as default
            if not selected_favorite['is_default']:
                if st.button("🏠 Set as Default", key=f"set_default_{method_prefix}"):
                    save_favorite_folder(
                        selected_favorite['name'],
                        selected_favorite['site_id'],
                        selected_favorite['path'],
                        is_default=True
                    )
                    st.success("Set as default folder!")
                    st.rerun()
        else:
            st.info("No favorite folders saved yet. Use 'Browse Folders' to add some!")
    
    elif folder_method == "🌳 Browse Folders":
        # Initialize folder browsing state
        if f'current_folder_path_{method_prefix}' not in st.session_state:
            st.session_state[f'current_folder_path_{method_prefix}'] = ""
            st.session_state[f'current_folder_id_{method_prefix}'] = None
        
        current_path = st.session_state[f'current_folder_path_{method_prefix}']
        current_folder_id = st.session_state[f'current_folder_id_{method_prefix}']
        
        # Breadcrumb navigation
        if current_path:
            path_parts = current_path.split('/')
            st.write("📍 **Navigation:**")
            breadcrumb_cols = st.columns(len(path_parts) + 1)
            
            with breadcrumb_cols[0]:
                if st.button("🏠 Root", key=f"breadcrumb_root_{method_prefix}"):
                    st.session_state[f'current_folder_path_{method_prefix}'] = ""
                    st.session_state[f'current_folder_id_{method_prefix}'] = None
                    st.rerun()
            
            for i, part in enumerate(path_parts):
                with breadcrumb_cols[i + 1]:
                    partial_path = '/'.join(path_parts[:i+1])
                    if st.button(f"📁 {part}", key=f"breadcrumb_{i}_{method_prefix}"):
                        st.session_state[f'current_folder_path_{method_prefix}'] = partial_path
                        # Clear the folder ID so it gets looked up again
                        st.session_state[f'current_folder_id_{method_prefix}'] = None
                        st.rerun()
        else:
            st.write("📍 **Current location**: Root")
        
        # Load current folder contents
        with st.spinner("Loading folders..."):
            folders = get_folder_tree(access_token, site_id, current_folder_id, current_path)
        
        if folders:
            st.write("📁 **Available Folders:**")
            
            # Display folders in a nice table-like format
            for i, folder in enumerate(folders):
                # Create a bordered container for each folder
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        folder_icon = "📂" if folder['hasChildren'] else "📁"
                        child_indicator = f" ({folder.get('childCount', '?')} items)" if folder['hasChildren'] else ""
                        st.write(f"{folder_icon} **{folder['name']}**{child_indicator}")
                        if folder['path'] != folder['name']:  # Show full path if different
                            st.caption(f"Path: {folder['path']}")
                    
                    with col2:
                        if st.button("📂 Open", key=f"open_{folder['id']}_{method_prefix}", help=f"Browse into {folder['name']}"):
                            st.session_state[f'current_folder_path_{method_prefix}'] = folder['path']
                            st.session_state[f'current_folder_id_{method_prefix}'] = folder['id']
                            st.rerun()
                    
                    with col3:
                        if st.button("🎯 Select", key=f"select_{folder['id']}_{method_prefix}", help=f"Upload to {folder['name']}"):
                            selected_folder_path = folder['path']
                            st.session_state[f'selected_folder_path_{method_prefix}'] = selected_folder_path
                            st.success(f"✅ Selected: **{folder['path']}**")
                            
                            # Option to save as favorite (in sidebar)
                            with st.expander("💾 Save as Favorite"):
                                fav_name = st.text_input(
                                    "Favorite Name",
                                    value=folder['name'],
                                    key=f"fav_name_{folder['id']}_{method_prefix}"
                                )
                                make_default = st.checkbox(
                                    "Set as default folder",
                                    key=f"make_default_{folder['id']}_{method_prefix}"
                                )
                                if st.button("💾 Save", key=f"save_fav_{folder['id']}_{method_prefix}"):
                                    save_favorite_folder(fav_name, site_id, folder['path'], make_default)
                                    st.success("Saved to favorites!")
                                    st.rerun()
                            break
                    
                    st.divider()  # Visual separator between folders
            
            # Show current selection status
            current_selection = st.session_state.get(f'selected_folder_path_{method_prefix}', '')
            if current_selection:
                st.info(f"🎯 **Currently Selected**: {current_selection}")
            else:
                st.warning("⚠️ No folder selected yet. Click 'Select' on a folder above.")
        else:
            st.info("No subfolders found in this location.")
            selected_folder_path = current_path
            st.session_state[f'selected_folder_path_{method_prefix}'] = selected_folder_path
    
    elif folder_method == "✏️ Enter Path":
        selected_folder_path = st.text_input(
            "Folder Path",
            value="Exam Procedures/ExamSoft/Import",
            placeholder="e.g., Exam Procedures/ExamSoft/Import",
            key=f"manual_folder_path_{method_prefix}",
            help="Enter the full folder path within the SharePoint site"
        )
        
        if selected_folder_path:
            # Option to save as favorite
            with st.expander("💾 Save as Favorite"):
                fav_name = st.text_input(
                    "Favorite Name",
                    value=selected_folder_path.split('/')[-1],
                    key=f"manual_fav_name_{method_prefix}"
                )
                make_default = st.checkbox(
                    "Set as default folder",
                    key=f"manual_make_default_{method_prefix}"
                )
                if st.button("💾 Save", key=f"manual_save_fav_{method_prefix}"):
                    save_favorite_folder(fav_name, site_id, selected_folder_path, make_default)
                    st.success("Saved to favorites!")
                    st.rerun()
    
    # Return the selected path (URL encode spaces)
    if selected_folder_path:
        # Store in session state for persistence
        st.session_state[f'final_folder_path_{method_prefix}'] = selected_folder_path
        return selected_folder_path.replace(' ', '%20') + ('/' if not selected_folder_path.endswith('/') else '')
    
    # Check if we have a stored selection
    stored_path = st.session_state.get(f'final_folder_path_{method_prefix}', '')
    if stored_path:
        return stored_path.replace(' ', '%20') + ('/' if not stored_path.endswith('/') else '')
    
    return ""

def send_notification_email(access_token, recipients, subject, body, uploaded_files):
    """Send email notification using Microsoft Graph API"""
    try:
        import requests
        
        # Clean recipient list
        clean_recipients = [email.strip() for email in recipients if email.strip()]
        
        if not clean_recipients:
            return False
        
        # Add file links to email body if any
        if uploaded_files:
            body += "\n\nFile Links:\n" + "\n".join(f"• {file}" for file in uploaded_files)
        
        # Prepare email data - use HTML format for better formatting
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body.replace('\n', '<br>')
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}} 
                    for email in clean_recipients
                ]
            },
            "saveToSentItems": "true"
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Send email via Microsoft Graph
        response = requests.post(
            'https://graph.microsoft.com/v1.0/me/sendMail',
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        print(f"📧 Email response: {response.status_code}")
        print(f"📧 Email response text: {response.text[:200]}")
        
        if response.status_code == 202:  # Accepted
            return True
        elif response.status_code == 403:
            print(f"❌ Email permission denied - check Mail.Send permission")
            return False
        elif response.status_code == 400:
            print(f"❌ Email bad request - check recipient addresses")
            return False
        else:
            print(f"❌ Email failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email exception: {str(e)}")
        return False

def render_results(SHAREPOINT_AVAILABLE, method_prefix=""):
    """Render the results section (shared between both methods)"""
    from safe_formatter import upload_to_sharepoint_corrected
    
    data = st.session_state.processed_data
    
    st.markdown("---")
    st.subheader("Download Files")
    
    # Preview
    if data['instructions_text']:
        st.subheader("Instructions Preview")
        st.text(data['instructions_text'][:500] + "..." if len(data['instructions_text']) > 500 else data['instructions_text'])
    
    st.subheader("Questions Preview (First 3)")
    for i, q in enumerate(data['questions_list'][:3]):
        st.text(q[:200] + "..." if len(q) > 200 else q)
        st.markdown("---")
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        if data['instructions_docx']:
            if st.checkbox("📄 Download Instructions (DOCX)", value=True, key=f"download_inst_{method_prefix}_cb"):
                st.download_button(
                    label="📄 Download Instructions",
                    data=data['instructions_docx'],
                    file_name=data['instructions_filename'],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key=f"download_inst_{method_prefix}_btn"
                )
        else:
            st.info("No instructions to download")
    
    with col2:
        if st.checkbox("📝 Download Exam (RTF)", value=True, key=f"download_exam_{method_prefix}_cb"):
            if data['exam_rtf_bytes']:
                st.download_button(
                    label="📝 Download Exam (LibreOffice API)",
                    data=data['exam_rtf_bytes'],
                    file_name=data['exam_filename'],
                    mime="text/rtf",
                    use_container_width=True,
                    key=f"download_exam_api_{method_prefix}_btn"
                )
            else:
                st.download_button(
                    label="📝 Download Exam (Basic RTF)",
                    data=data['exam_rtf_content'],
                    file_name=data['exam_filename'],
                    mime="text/rtf",
                    use_container_width=True,
                    key=f"download_exam_basic_{method_prefix}_btn"
                )

    # SharePoint Upload
    if SHAREPOINT_AVAILABLE:
        st.markdown("---")
        st.subheader("📤 Upload to SharePoint (Optional)")
        
        is_authenticated = st.session_state.get('sp_authenticated', False)
        
        if is_authenticated:
            # Load available SharePoint sites dynamically
            st.write("🌐 **Choose SharePoint Site:**")
            
            if 'available_sites' not in st.session_state:
                with st.spinner("Loading available SharePoint sites..."):
                    access_token = st.session_state.get('sp_access_token')
                    sites = get_available_sharepoint_sites(access_token)
                    st.session_state.available_sites = sites
            
            sites = st.session_state.available_sites
            
            if sites:
                site_options = [f"{site['displayName']} ({site['webUrl']})" for site in sites]
                selected_site_display = st.selectbox(
                    "Select SharePoint Site",
                    options=site_options,
                    key=f"sharepoint_site_{method_prefix}",
                    help="Choose which SharePoint site to upload to"
                )
                
                # Find selected site data
                selected_site_index = site_options.index(selected_site_display)
                selected_site_data = sites[selected_site_index]
                
                st.info(f"📍 **Selected**: {selected_site_data['displayName']}")
                st.write(f"🔗 **URL**: {selected_site_data['webUrl']}")
                
                # Advanced folder browser
                selected_folder_path = render_folder_browser(
                    st.session_state.get('sp_access_token'), 
                    selected_site_data['id'], 
                    method_prefix
                )
                    
                site_info = {
                    'site_id': selected_site_data['id'],
                    'path': selected_folder_path
                } if selected_folder_path else None
            else:
                st.error("❌ Could not load SharePoint sites. Check permissions.")
                site_info = None
            
            # Refresh button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔄 Refresh", key=f"refresh_sites_{method_prefix}"):
                    st.session_state.pop('available_sites', None)
                    st.session_state.pop('available_folders', None)
                    st.rerun()
            
            if site_info:
                st.write("✅ **Ready to upload!** Select files to upload to SharePoint:")
                
                upload_instructions_sp = st.checkbox("📄 Upload Instructions to SharePoint", key=f"upload_inst_sp_{method_prefix}_cb") if data['instructions_docx'] else False
                upload_exam_sp = st.checkbox("📝 Upload Exam to SharePoint", value=True, key=f"upload_exam_sp_{method_prefix}_cb")
            else:
                upload_instructions_sp = False
                upload_exam_sp = False
            
            # Email functionality
            st.write("📧 **Email Options (Optional):**")
            
            # Quick email permission check
            email_available = True
            if 'email_permission_checked' not in st.session_state:
                try:
                    headers = {'Authorization': f'Bearer {st.session_state.get("sp_access_token")}'}
                    test_response = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders', headers=headers, timeout=10)
                    email_available = test_response.status_code == 200
                    st.session_state.email_permission_checked = email_available
                except:
                    email_available = False
                    st.session_state.email_permission_checked = False
            else:
                email_available = st.session_state.email_permission_checked
            
            if not email_available:
                st.warning("⚠️ Email permissions not available.")
                st.info("💡 **Solution**: Sign out and sign back in to refresh your token with the new Mail.Send permission.")
                
                # Button to clear the permission check cache
                if st.button("🔄 Recheck Email Permissions", key=f"recheck_email_{method_prefix}"):
                    st.session_state.pop('email_permission_checked', None)
                    st.rerun()
                
                send_email = False
            else:
                send_email = st.checkbox("Send email notification", key=f"send_email_{method_prefix}_cb")
            
            email_recipients = ""
            email_subject = ""
            email_body = ""
            
            if send_email:
                col1, col2 = st.columns(2)
                with col1:
                    email_recipients = st.text_area(
                        "Recipients (one email per line)", 
                        placeholder="john.doe@charlestonlaw.edu\njane.smith@charlestonlaw.edu",
                        key=f"email_recipients_{method_prefix}",
                        height=100
                    )
                with col2:
                    email_subject = st.text_input(
                        "Email Subject", 
                        value=f"ExamSoft Files Ready: {data.get('exam_filename', 'Exam')}",
                        key=f"email_subject_{method_prefix}"
                    )
                
                email_body = st.text_area(
                    "Email Message", 
                    value=f"""The ExamSoft files have been processed and are ready for use.

Files generated:
• Exam: {data.get('exam_filename', 'exam file')}
{f"• Instructions: {data.get('instructions_filename', 'instructions file')}" if data.get('instructions_docx') else ""}

Questions: {data.get('mc_count', 0)} multiple choice, {data.get('essay_count', 0)} essay

This email was sent automatically by the ExamSoft RTF Formatter tool.""",
                    key=f"email_body_{method_prefix}",
                    height=150
                )
            
            if site_info and st.button("🚀 Upload to SharePoint", use_container_width=True, key=f"sharepoint_upload_{method_prefix}_btn"):
                try:
                    with st.spinner("Processing upload and email..."):
                        access_token = st.session_state.get('sp_access_token')
                        
                        upload_results = []
                        
                        # Upload instructions with selected site
                        if upload_instructions_sp and data['instructions_docx']:
                            success, result = upload_to_sharepoint_with_site(
                                access_token, 
                                data['instructions_docx'], 
                                data['instructions_filename'],
                                site_info['site_id'],
                                site_info['path']
                            )
                            upload_results.append(("Instructions", success, result))
                        
                        # Upload exam with selected site
                        if upload_exam_sp:
                            rtf_content = data.get('exam_rtf_bytes') or data.get('exam_rtf_content')
                            if rtf_content:
                                success, result = upload_to_sharepoint_with_site(
                                    access_token, 
                                    rtf_content, 
                                    data['exam_filename'],
                                    site_info['site_id'],
                                    site_info['path']
                                )
                                upload_results.append(("Exam", success, result))
                        
                        # Show upload results
                        uploaded_files = []
                        for file_type, success, result in upload_results:
                            if success:
                                st.success(f"✅ {file_type} uploaded to SharePoint!")
                                if isinstance(result, dict) and 'url' in result:
                                    st.write(f"🔗 **{file_type} URL:** {result['url']}")
                                    uploaded_files.append(f"{file_type}: {result['url']}")
                            else:
                                st.error(f"❌ Failed to upload {file_type}: {result}")
                        
                        # Send email if requested
                        if send_email and email_recipients.strip():
                            try:
                                email_success = send_notification_email(
                                    access_token,
                                    email_recipients.strip().split('\n'),
                                    email_subject,
                                    email_body,
                                    uploaded_files
                                )
                                if email_success:
                                    st.success("✅ Email notifications sent!")
                                else:
                                    st.warning("⚠️ Upload successful but email failed")
                            except Exception as email_error:
                                st.warning(f"⚠️ Upload successful but email failed: {str(email_error)}")
                        
                        if all(success for _, success, _ in upload_results):
                            st.balloons()
                except Exception as e:
                    st.error(f"Process error: {str(e)}")
        else:
            st.info("🔐 **Sign in with Microsoft 365** in the sidebar to upload to SharePoint")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🔄 Convert Another Exam", use_container_width=True, key=f"convert_another_{method_prefix}_btn"):
            st.session_state.processed_data = None
            st.success("📝 Form cleared! Ready for next exam.")
            st.rerun()

def main():
    """Main application function"""
    try:
        # Try to import SharePoint functionality
        try:
            from persistent_auth import initialize_persistent_auth, render_persistent_auth_ui, render_auth_status, sign_out_persistent
            SHAREPOINT_AVAILABLE = True
        except (ImportError, AttributeError):
            SHAREPOINT_AVAILABLE = False

        # Main UI
        st.subheader("Charleston School of Law")
        st.header("ExamSoft RTF Formatter")
        
        # Help System for Non-Technical Users
        with st.expander("🆘 Need Help? Click here for step-by-step guidance", expanded=False):
            st.markdown("""
            ### 👋 Welcome! This tool converts your exam questions into ExamSoft RTF format.
            
            **🎯 What you need to get started:**
            - Your exam questions (typed or in a document)
            - Your answer key (A, B, C, D answers for each question)
            - Course information (course code, section, professor name)
            
            ---
            
            ### 📋 Step-by-Step Instructions:
            
            **Method 1: Text Paste (Easiest for beginners)**
            1. 📝 **Course Info**: Fill in course code (like "CONST"), section ("001"), and professor name
            2. 📄 **Instructions**: Copy/paste your exam instructions (optional)
            3. ❓ **Questions**: Copy/paste all your exam questions with answer choices
            4. 🔤 **Answer Key**: Copy/paste your answers (one per line: A, B, C, D, etc.)
            5. 🚀 **Click "Generate RTF"** - that's it!
            
            **Method 2: File Upload (For advanced users)**
            1. 📤 Upload your Word doc, text file, or Excel answer key
            2. 📝 Fill in course information
            3. 🚀 Click "Generate RTF"
            
            ---
            
            ### 💡 Pro Tips:
            - **Answer Key Format**: Just list the letters (A, B, C, D) one per line - no headers needed
            - **Excel Files**: Put answers in the first column, one answer per row
            - **Questions**: Include the question number and all answer choices (A, B, C, D)
            - **Save Time**: Use SharePoint integration to automatically save files to the IT folder
            
            ---
            
            ### 🆘 Having Problems?
            **Common Issues & Solutions:**
            - **"Wrong number of answers"**: Make sure your answer key has exactly one answer per question
            - **"Email not working"**: Sign out and sign back in to refresh permissions
            - **"File upload failed"**: Try copying and pasting the text instead
            
            **Still stuck?** Contact IT support - they can help you get set up!
            """)
        
        # Method selection tabs
        tab1, tab2 = st.tabs(["📝 Text Paste Method", "📁 File Upload Method"])
        
        with tab1:
            st.write("Paste your instructions, exam questions, and answer key below. No file upload needed.")
            render_text_paste_method()
            
        with tab2:
            st.write("Upload docx, rtf, text, csv, or xlsx files to extract and format your exam content.")
            render_file_upload_method()

        # SharePoint authentication in sidebar
        if SHAREPOINT_AVAILABLE:
            try:
                if 'auth_initialized' not in st.session_state:
                    initialize_persistent_auth()
                    st.session_state.auth_initialized = True
                    
                with st.sidebar:
                    st.header("🔐 Microsoft 365")
                    is_authenticated = render_persistent_auth_ui()
                    
                    if is_authenticated:
                        render_auth_status()
                        if st.button("🔓 Sign Out", key="sidebar_signout"):
                            if sign_out_persistent():
                                st.success("👋 Signed out!")
                                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Auth error: {e}")

    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.error("Please ensure all required packages are installed.")
        st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"❌ Application Error: {e}")
        st.code(traceback.format_exc())

# Run the main function
if __name__ == "__main__":
    main()
else:
    # When imported, still run main (for streamlit run)
    main()