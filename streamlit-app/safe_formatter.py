"""
Safe formatter that imports functions from the original examsoft_formatter_updated.py
without executing the problematic UI code
"""

# Import all the good functions we need
import sys
import os

# Add a flag to prevent UI execution
os.environ['STREAMLIT_IMPORT_ONLY'] = '1'

# Now we can safely import the functions
from examsoft_formatter_updated import (
    generate_docx_with_questions,
    convert_docx_to_rtf_via_api, 
    generate_filename,
    clean_text_encoding,
    generate_instructions_docx,
    parse_questions_from_text,
    parse_answer_key_with_header_detection,
    create_rtf_content,
    format_multiple_choice_question,
    format_essay_question,
    classify_question
)

try:
    from examsoft_formatter_updated import upload_to_sharepoint_corrected
except (ImportError, AttributeError):
    def upload_to_sharepoint_corrected(access_token, file_content, filename):
        return False, "SharePoint upload not available"

try:
    from examsoft_formatter_updated import get_converter_endpoint, is_using_azure
except (ImportError, AttributeError):
    def get_converter_endpoint():
        return "http://localhost:8080/convert"
    
    def is_using_azure():
        return False

# Clean up the environment variable
if 'STREAMLIT_IMPORT_ONLY' in os.environ:
    del os.environ['STREAMLIT_IMPORT_ONLY']

# Export all the functions we need
__all__ = [
    'generate_docx_with_questions',
    'convert_docx_to_rtf_via_api', 
    'generate_filename',
    'clean_text_encoding',
    'generate_instructions_docx',
    'parse_questions_from_text',
    'parse_answer_key_with_header_detection',
    'create_rtf_content',
    'format_multiple_choice_question',
    'format_essay_question',
    'classify_question',
    'upload_to_sharepoint_corrected',
    'get_converter_endpoint',
    'is_using_azure'
]