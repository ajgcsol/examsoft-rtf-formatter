from flask import Flask, request, send_file
import subprocess
import os
import re

app = Flask(__name__)

def clean_rtf_content(rtf_path):
    """Clean up RTF content to fix encoding and formatting issues"""
    try:
        # Read the RTF file
        with open(rtf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Fix common encoding issues
        content = content.replace('â€™', "'")  # Fix apostrophes
        content = content.replace('â€œ', '"')  # Fix opening quotes
        content = content.replace('â€', '"')   # Fix closing quotes
        content = content.replace('â€"', '—')  # Fix em dash
        content = content.replace('â€"', '–')  # Fix en dash
        content = content.replace('Â', '')     # Remove unwanted Â characters
        
        # Clean up excessive RTF formatting codes that can cause display issues
        # Remove some problematic RTF codes while keeping basic formatting
        content = re.sub(r'\\lang\d+', '', content)  # Remove language codes
        content = re.sub(r'\\f\d+', '', content)     # Remove font references
        
        # Write cleaned content back
        with open(rtf_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"Warning: Could not clean RTF content: {e}")
        # Continue anyway with original file

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'healthy', 'service': 'LibreOffice Converter'}

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    docx_path = '/tmp/input.docx'
    rtf_path = '/tmp/input.rtf'  # LibreOffice creates output with same name as input
    file.save(docx_path)
    
    # Run LibreOffice conversion with better options for text encoding
    subprocess.run([
        'libreoffice', 
        '--headless', 
        '--convert-to', 
        'rtf',
        '--outdir', 
        '/tmp',
        docx_path
    ], check=True)
    
    # Clean up the RTF content to fix encoding issues
    clean_rtf_content(rtf_path)
    
    return send_file(rtf_path, as_attachment=True, download_name='converted.rtf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
