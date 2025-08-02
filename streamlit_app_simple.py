import streamlit as st
import sys
import traceback

# Configure page
st.set_page_config(
    page_title="ExamSoft RTF Formatter - Test",
    page_icon="📝",
    layout="wide"
)

st.title("ExamSoft RTF Formatter - Debug Version")

# Initialize session state
if 'test_data' not in st.session_state:
    st.session_state.test_data = None

if 'click_count' not in st.session_state:
    st.session_state.click_count = 0

# Simple form inputs
st.subheader("Basic Form Test")

course_input = st.text_input("Course", placeholder="e.g., CONST", key="course_simple")
section_input = st.text_input("Section", placeholder="e.g., 001", key="section_simple")

# Simple text area
questions_input = st.text_area("Questions", height=200, key="questions_simple")

# Test button with minimal processing
if st.button("Test Process", key="test_process_btn"):
    try:
        st.session_state.click_count += 1
        st.session_state.test_data = {
            'course': course_input,
            'section': section_input,
            'questions': questions_input,
            'processed_at': str(st.session_state.click_count)
        }
        st.success(f"✅ Processed successfully! Click #{st.session_state.click_count}")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.code(traceback.format_exc())

# Show results if data exists
if st.session_state.test_data:
    st.subheader("Results")
    st.json(st.session_state.test_data)
    
    # Test download button
    if st.button("Test Download", key="test_download_btn"):
        st.success("Download button clicked!")
    
    # Test clear button
    if st.button("Clear Data", key="clear_data_btn"):
        st.session_state.test_data = None
        st.session_state.click_count = 0
        st.success("Data cleared!")
        st.rerun()

# Sidebar test
with st.sidebar:
    st.header("Sidebar Test")
    if st.button("Sidebar Button", key="sidebar_btn"):
        st.success("Sidebar button works!")

st.write("---")
st.write("**Debug Info:**")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")
st.write(f"Session state keys: {list(st.session_state.keys())}")