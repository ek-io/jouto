import streamlit as st
import yaml
import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.discovery import load_config, get_config_path

st.set_page_config(page_title="Profile Setup", page_icon="👤", layout="wide")

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("👤 Applicant Profile")
st.write("Manage your personal details, skills, and resume. This data powers the AI evaluator and the auto-applier.")

config_data = load_config()
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
            
            with open(get_config_path(), "w") as f:
                yaml.dump(config_data, f)
            st.success("Details saved successfully!")

with col2:
    st.subheader("📄 Resume Upload")
    st.write("Upload your PDF resume. The auto-applier will use this file when filling out applications.")
    
    current_resume = config_data.get('resume_path', '')
    if current_resume and os.path.exists(current_resume):
        st.success(f"Current Resume: **{os.path.basename(current_resume)}**")
    else:
        st.warning("No resume uploaded yet.")
        
    uploaded_file = st.file_uploader("Upload New Resume", type=["pdf"])
    if uploaded_file is not None:
        data_dir = os.path.dirname(get_config_path())
        save_path = os.path.join(data_dir, uploaded_file.name)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        config_data['resume_path'] = save_path
        with open(get_config_path(), "w") as f:
            yaml.dump(config_data, f)
            
        st.success(f"Resume '{uploaded_file.name}' saved and linked to your profile!")
        st.rerun()

st.divider()
with st.expander("Advanced Configuration (Raw YAML)"):
    st.write("Edit work history and education manually here.")
    config_yaml_str = yaml.dump(config_data, sort_keys=False)
    edited_yaml = st.text_area("Master YAML Profile", config_yaml_str, height=400)
    
    if st.button("Save Raw YAML"):
        try:
            new_config = yaml.safe_load(edited_yaml)
            with open(get_config_path(), "w") as f:
                yaml.dump(new_config, f)
            st.success("Raw profile saved successfully!")
            st.rerun()
        except yaml.YAMLError as e:
            st.error(f"Invalid YAML format: {e}")

