from pathlib import Path
import streamlit as st
import pandas as pd
import docx
import re
from io import BytesIO

# Helper to extract text from DOCX
def extract_text_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Determine file type and extract text
def extract_text(file):
    suffix = Path(file.name).suffix.lower()
    if suffix == ".docx":
        return extract_text_docx(file)
    elif suffix == ".rtf":
        raw = file.read().decode('utf-8', errors='ignore')
        text = re.sub(r'{\\[^}]+}|\\[a-z]+\\d* ?', '', raw)
        return re.sub(r'[{}]', '', text)
    else:
        return file.read().decode('utf-8', errors='ignore')

# Clean and format question text
def format_question_block(block, answer_key):
    lines = block.strip().splitlines()
    if not lines:
        return ""

    formatted = []
    current_qnum = ""
    is_essay = False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if i == 0 and line.lower().startswith("type:"):
            formatted.append(line)
            is_essay = line.lower().startswith("type: e")
        elif re.match(r"^\d+[.)]", line):
            current_qnum = re.match(r"^(\d+)[.)]", line).group(1)
            formatted.append(line)
        elif re.match(r"^[a-dA-D][.)]", line):
            if not is_essay:
                choice_letter = line[0].upper()
                answer = answer_key.get(current_qnum, "")
                if choice_letter == answer:
                    formatted.append(f"*{line}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        else:
            if formatted:
                formatted[-1] += "<br>" + line
            else:
                formatted.append(line)

    return "\n".join(formatted)

# Load answer key
def load_answer_key(file):
    ext = Path(file.name).suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(file)
    elif ext == ".xlsx":
        df = pd.read_excel(file, engine="openpyxl")
    else:
        return {}
    return {str(i+1): str(row[0]).strip().upper() for i, row in df.iterrows()}

# Streamlit UI
st.title("ExamSoft RTF Formatter")

exam_file = st.file_uploader("Upload Exam File (.docx or .rtf)", type=["docx", "rtf"])
answer_file = st.file_uploader("Upload Answer Key (.xlsx or .csv)", type=["xlsx", "csv"])

if exam_file and answer_file:
    exam_text = extract_text(exam_file)
    answer_key = load_answer_key(answer_file)

    # Split into instructions and questions
    instructions_text = exam_text.split("MULTIPLE-CHOICE")[0].strip()
    questions_text = exam_text.split("MULTIPLE-CHOICE")[-1].strip()

    # Split questions by number pattern
    question_blocks = re.split(r"\n(?=\d+[.)])", questions_text)
    formatted_questions = []

    for block in question_blocks:
        match = re.match(r"(\d+)[.)]", block.strip())
        current_qnum = match.group(1) if match else ""
        formatted = format_question_block(block, answer_key)
        if formatted:
            formatted_questions.append(formatted)

    # Save instructions RTF (no HTML tags)
    instructions_rtf = "{\\rtf1\\ansi\n" + instructions_text.replace("\n", "\\line ") + "}"
    instructions_bytes = BytesIO(instructions_rtf.encode("utf-8"))
    st.download_button("Download Instructions RTF", instructions_bytes, file_name="Instructions.rtf")

    # Save formatted questions RTF
    formatted_rtf = "{\\rtf1\\ansi\n" + "\\line \\line ".join(formatted_questions) + "}"
    formatted_bytes = BytesIO(formatted_rtf.encode("utf-8"))
    st.download_button("Download Formatted Exam RTF", formatted_bytes, file_name="Formatted_ExamSoft_Import.rtf")
