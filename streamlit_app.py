import streamlit as st

# Configure page
st.set_page_config(
    page_title="ExamSoft RTF Formatter - Charleston School of Law",
    page_icon="📝",
    layout="wide"
)

# Import the main app
from examsoft_formatter_updated import *

# This ensures the app runs when deployed to Streamlit Cloud
