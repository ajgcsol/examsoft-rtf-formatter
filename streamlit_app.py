import streamlit as st
import sys
import traceback

# Configure page
st.set_page_config(
    page_title="ExamSoft RTF Formatter - Charleston School of Law",
    page_icon="📝",
    layout="wide"
)

# Import and run the main app with error handling
try:
    # Import the main app module - this runs the UI automatically
    import examsoft_formatter_updated
    
    # The module runs automatically on import since the UI code is at module level
    # This is the expected behavior for Streamlit apps
    
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure all required packages are installed:")
    st.code("""
Required packages from requirements.txt:
- streamlit>=1.25.0
- pandas>=1.5.0
- requests>=2.28.0
- python-docx>=0.8.11
- striprtf>=0.0.26
- msal>=1.20.0
- requests-oauthlib>=1.3.0
- office365-rest-python-client>=2.5.0
    """)
    
    # Show system information only on error
    st.write("**System Information:**")
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    
    # Show detailed error info
    with st.expander("🔍 Detailed Error Information"):
        st.code(traceback.format_exc())
    
    st.stop()

except Exception as e:
    st.error(f"❌ Application Error: {e}")
    
    # Show system info for debugging
    st.write("**System Information:**")
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    
    # Show detailed error info
    with st.expander("🔍 Full Error Traceback"):
        st.code(traceback.format_exc())
    
    st.info("💡 **Troubleshooting Tips:**")
    st.write("1. Check that all packages in requirements.txt are installed")
    st.write("2. Verify that Streamlit secrets are properly configured")
    st.write("3. Ensure all configuration files are present")
    
    st.stop()
