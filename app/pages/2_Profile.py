import streamlit as st
from PIL import Image
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_user_profile, update_user_profile

st.set_page_config(page_title="Jouto | Profile", page_icon=Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if 'pages' in __file__ else os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.jpg')), layout="wide", initial_sidebar_state="expanded")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("👤 Applicant Profile")
st.write("Manage your personal details, skills, and resume. This data powers the AI evaluator and the auto-applier.")

config_data, current_resume, _ = get_user_profile(st.session_state.user_id)
if "personal_details" not in config_data:
    config_data["personal_details"] = {}

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Basic Information")
    with st.form("basic_info_form"):
        first_name = st.text_input("First Name", config_data['personal_details'].get('first_name', ''))
        last_name = st.text_input("Last Name", config_data['personal_details'].get('last_name', ''))
        email = st.text_input("Email", config_data['personal_details'].get('email', ''))
        phone = st.text_input("Phone", config_data['personal_details'].get('phone', ''))
        location = st.text_input("Location", config_data['personal_details'].get('location', ''))
        
        target_titles = st.text_input("Target Job Titles (comma separated)", ", ".join(config_data.get('target_titles', [])))
        skills = st.text_area("Core Skills (comma separated)", ", ".join(config_data.get('skills', [])))
        
        submit_basic = st.form_submit_button("Save Details", type="primary")
        if submit_basic:
            config_data['personal_details']['first_name'] = first_name
            config_data['personal_details']['last_name'] = last_name
            config_data['personal_details']['email'] = email
            config_data['personal_details']['phone'] = phone
            config_data['personal_details']['location'] = location
            config_data['target_titles'] = [t.strip() for t in target_titles.split(",") if t.strip()]
            config_data['skills'] = [s.strip() for s in skills.split(",") if s.strip()]
            
            update_user_profile(st.session_state.user_id, config_data)
            st.success("Details saved successfully!")

with col2:
    st.subheader("📄 Resume Upload (Cloud)")
    st.write("Upload your PDF resume. It will be saved securely in the cloud database.")
    
    if current_resume:
        st.success(f"Current Resume: **{current_resume}**")
    else:
        st.warning("No resume uploaded yet.")
        
    uploaded_file = st.file_uploader("Upload New Resume", type=["pdf"])
    if uploaded_file is not None:
        resume_bytes = uploaded_file.getvalue()
        update_user_profile(st.session_state.user_id, config_data, uploaded_file.name, resume_bytes)
        st.success(f"Resume '{uploaded_file.name}' saved to the cloud!")
        st.rerun()

st.divider()
with st.expander("Advanced Configuration (Raw JSON)"):
    st.write("Edit work history and education manually here.")
    config_json_str = json.dumps(config_data, indent=2)
    edited_json = st.text_area("Master JSON Profile", config_json_str, height=400)
    
    if st.button("Save Raw JSON"):
        try:
            new_config = json.loads(edited_json)
            update_user_profile(st.session_state.user_id, new_config)
            st.success("Raw profile saved successfully!")
            st.rerun()
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")
