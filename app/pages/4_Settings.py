import streamlit as st
from PIL import Image
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from core.database import (If we need any settings db calls later)

st.set_page_config(page_title="Jouto | Settings", page_icon=Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if 'pages' in __file__ else os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.jpg')), layout="wide", initial_sidebar_state="expanded")

if "user_id" not in st.session_state or st.session_state.user_id is None:
        st.markdown('''
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }
        </style>
    ''', unsafe_allow_html=True)
    st.warning("Please log in on the Dashboard first.")
    st.stop()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("⚙️ Account Settings")
st.write("Manage your account preferences and security.")

st.divider()

st.subheader("Security")
with st.container(border=True):
    st.text_input("Change Password", type="password")
    st.text_input("Confirm New Password", type="password")
    if st.button("Update Password"):
        st.info("Password update functionality will be enabled in the next update!")

st.divider()

st.subheader("Danger Zone")
with st.container(border=True):
    st.write("Permanently delete your account and all associated data, including your cloud resume and application history.")
    if st.button("Delete Account", type="primary"):
        st.error("Account deletion requires admin confirmation currently.")
