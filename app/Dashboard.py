import streamlit as st
import os
import sys

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import initialize_db

st.set_page_config(
    page_title="AutoApply Agent V2",
    page_icon="🚀",
    layout="wide"
)

# Initialize database
initialize_db()

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("🚀 AutoApply Agent Dashboard")

st.markdown("""
Welcome to **AutoApply Agent V2**, your automated job search assistant.

### Features
* **👤 Profile**: Manage your resume data and target roles.
* **🔍 Discovery**: Find and evaluate jobs across the web using Gemini AI.
* **🚀 Auto Apply**: Use Playwright to automatically fill out application forms.
* **📊 History**: Track all the applications you've saved and submitted.

Please configure your **Gemini API Key** in the sidebar to enable AI features!
""")

if "GEMINI_API_KEY" in os.environ:
    st.sidebar.success("✅ AI Engine Active (API Key configured securely)")
else:
    api_key = st.sidebar.text_input("Gemini API Key (Admin)", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    else:
        st.sidebar.warning("API Key missing. AI features disabled.")
