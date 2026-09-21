import streamlit as st
import yaml
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.discovery import load_config, get_config_path

st.set_page_config(page_title="Profile Setup", page_icon="👤", layout="wide")

st.title("👤 Profile Setup")
st.write("Configure your master profile data. This information will be used by the AI to evaluate job matches and auto-fill applications.")

try:
    config_data = load_config()
    config_yaml_str = yaml.dump(config_data, sort_keys=False)
    edited_yaml = st.text_area("Master YAML Profile", config_yaml_str, height=500)
    
    if st.button("Save Profile Data", type="primary"):
        try:
            new_config = yaml.safe_load(edited_yaml)
            with open(get_config_path(), "w") as f:
                yaml.dump(new_config, f)
            st.success("Profile saved successfully!")
        except yaml.YAMLError as e:
            st.error(f"Invalid YAML format: {e}")
except Exception as e:
    st.error(f"Error loading profile: {e}")
