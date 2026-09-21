import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.applier import apply_to_job
from core.database import get_applications, update_status

st.set_page_config(page_title="Auto Apply", page_icon="🚀", layout="wide")

st.title("🚀 Auto Apply Engine")
st.write("Automatically fill out job applications using Playwright. Select a saved job from your history or paste a custom URL.")

job_url = st.text_input("Job Application URL")

if st.button("Start Playwright Engine", type="primary"):
    if job_url:
        st.info("Launching browser... Please do not interact with the browser until it pauses.")
        try:
            apply_to_job(job_url)
            st.success("Application process paused for review. Check the Playwright window.")
        except Exception as e:
            st.error(f"Error during application: {e}")
    else:
        st.warning("Please enter a valid URL.")

st.divider()
st.subheader("Apply to Saved Jobs")
apps = get_applications()
saved_apps = [app for app in apps if app['status'] == 'Saved']

if saved_apps:
    for app in saved_apps:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{app['title']}** - [Link]({app['url']})")
        with col2:
            if st.button("Auto Apply", key=f"apply_{app['id']}"):
                try:
                    apply_to_job(app['url'])
                    update_status(app['id'], "Applied")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.info("No saved jobs found. Go to the Discovery page to find and save jobs.")
