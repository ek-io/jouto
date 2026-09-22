import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_user_applications, update_user_job_status
from app.components.navbar import render_navbar

st.set_page_config(page_title="Jouto | History", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()
    
render_navbar()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 My Application History")
st.write("Track the status of all your saved and submitted applications.")

apps = get_user_applications(st.session_state.user_id)

if not apps:
    st.info("You haven't saved or applied to any jobs yet. Head to the Discovery tab to get started.")
else:
    col1, col2, col3 = st.columns(3)
    
    saved = [a for a in apps if a['status'] == 'Saved']
    applied = [a for a in apps if a['status'] == 'Applied']
    interviewing = [a for a in apps if a['status'] == 'Interviewing']
    
    with col1:
        st.subheader(f"📌 Saved ({len(saved)})")
        for app in saved:
            with st.container(border=True):
                st.markdown(f"**{app['title']}** at {app['company']}")
                st.caption(f"Fit Score: {app['fit_score']}/100")
                if st.button("Mark Applied", key=f"ma_{app['uj_id']}", use_container_width=True):
                    update_user_job_status(app['uj_id'], "Applied")
                    st.rerun()
                    
    with col2:
        st.subheader(f"🚀 Applied ({len(applied)})")
        for app in applied:
            with st.container(border=True):
                st.markdown(f"**{app['title']}** at {app['company']}")
                st.caption(f"Applied: {app['applied_date'][:10]}")
                if st.button("Mark Interviewing", key=f"mi_{app['uj_id']}", use_container_width=True):
                    update_user_job_status(app['uj_id'], "Interviewing")
                    st.rerun()
                    
    with col3:
        st.subheader(f"🎯 Interviewing ({len(interviewing)})")
        for app in interviewing:
            with st.container(border=True):
                st.markdown(f"**{app['title']}** at {app['company']}")
                if st.button("Mark Rejected", key=f"mr_{app['uj_id']}", use_container_width=True):
                    update_user_job_status(app['uj_id'], "Rejected")
                    st.rerun()
