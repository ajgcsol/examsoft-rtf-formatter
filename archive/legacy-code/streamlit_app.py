# Import and run the fixed main app
try:
    from streamlit_app_fixed import main
    main()
except ImportError as e:
    import streamlit as st
    import sys
    import traceback
    
    # Configure page
    st.set_page_config(
        page_title="ExamSoft RTF Formatter - Charleston School of Law",
        page_icon="📝",
        layout="wide"
    )
    
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
    
    st.write("**System Information:**")
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    
    with st.expander("🔍 Detailed Error Information"):
        st.code(traceback.format_exc())
    
except Exception as e:
    import streamlit as st
    import sys
    import traceback
    
    st.error(f"❌ Application Error: {e}")
    st.write("**System Information:**")
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    
    with st.expander("🔍 Full Error Traceback"):
        st.code(traceback.format_exc())
    
    st.info("💡 **Troubleshooting Tips:**")
    st.write("1. Check that all packages in requirements.txt are installed")
    st.write("2. Verify that Streamlit secrets are properly configured")
    st.write("3. Ensure all configuration files are present")
