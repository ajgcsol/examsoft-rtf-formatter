from pathlib import Path
import streamlit as st
import pandas as pd
import re
import os
from docx import Document
from io import BytesIO

# Helper function to clean and format instructions
def extract_instructions(text):
    lines = text.splitlines()
    start = 0
    end = 0
    for i, line in enumerate(lines):
        if "INSTRUCTIONS" in line.upper():
            start = i
        if "MULTIPLE-CHOICE" in line.upper():
            end = i
            break
    instructions = lines[start:end]
    cleaned = "<br>".join([line.strip() for line in instructions if line.strip()])
    return cleaned

# Helper function to extract questions and format them
def format_questions(text, answers):
    questions = []
    q_blocks = re.split(r'\n\d+\.', text)
    for i, block in enumerate(q_blocks[1:], start=1):
        lines = block.strip().splitlines()
        question_text = f"{i}. " + "<br>".join(lines)
        correct = answers[i-1] if i-1 < len(answers) else ""
        pattern = re.compile(rf"^({correct})\.", re.IGNORECASE)
        question_text = pattern.sub(r"*\1.", question_text)
        questions.append(question_text)
    return "\n\n".join(questions)

# Streamlit UI
st.title("ExamSoft RTF Formatter")

exam_file = st.file_uploader("Upload Exam File (.rtf, .docx)", type=["rtf", "docx"])
answer_file = st.file_uploader("Upload Answer File (.xlsx, .csv)", type=["xlsx", "csv"])

if exam_file and answer_file:
    # Read exam text
    if exam_file.name.endswith(".rtf"):
        raw_bytes = exam_file.read()
        raw_text = raw_bytes.decode("utf-8", errors="ignore")
        # Strip RTF control words
        raw_text = re.sub(r"{\\[^}]+}", "", raw_text)
        raw_text = re.sub(r"\\[a-z]+\d*", "", raw_text)
        raw_text = re.sub(r"[{}]", "", raw_text)
    elif exam_file.name.endswith(".docx"):
        doc = Document(exam_file)
        raw_text = "\n".join([p.text for p in doc.paragraphs])
    else:
        st.error("Unsupported exam file format.")
        st.stop()

    # Read answers
    if answer_file.name.endswith(".xlsx"):
        df = pd.read_excel(answer_file, engine="openpyxl", header=None)
    elif answer_file.name.endswith(".csv"):
        df = pd.read_csv(answer_file, header=None)
    else:
        st.error("Unsupported answer file format.")
        st.stop()

    answer_list = df.iloc[:, 0].astype(str).tolist()

    # Process instructions and questions
    instructions_html = extract_instructions(raw_text)
    questions_text = format_questions(raw_text, answer_list)

    # Create RTF content
    def to_rtf(text):
        return r"{\rtf1\ansi\deff0 " + text.replace("\n", r"\par ") + "}"

    instructions_rtf = to_rtf(instructions_html)
    questions_rtf = to_rtf(questions_text)

    # Download buttons
    st.download_button("Download Instructions RTF", instructions_rtf.encode("utf-8"), file_name="instructions.rtf")
    st.download_button("Download Formatted Exam RTF", questions_rtf.encode("utf-8"), file_name="formatted_exam.rtf")
