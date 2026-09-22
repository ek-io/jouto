import streamlit as st
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.applier import apply_to_job
from core.database import get_user_applications, update_user_job_status, get_user_profile

st.set_page_config(page_title="Auto Apply", page_icon="🚀", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()

st.title("🚀 Application Engine")
st.write("Automatically fill out job applications using Playwright. Choose between manual review or full bulk mode.")

user_profile, resume_path = get_user_profile(st.session_state.user_id)
# Ensure resume_path is in the config dict for the applier to use
user_profile['resume_path'] = resume_path

# Single URL Manual Apply
with st.expander("Manual URL Apply (Safe Mode)"):
    job_url = st.text_input("Job Application URL")
    if st.button("Start Playwright Engine", type="primary"):
        if job_url:
            st.info("Launching browser... Please do not interact with the browser until it pauses.")
            try:
                apply_to_job(job_url, user_profile, bulk_mode=False)
                st.success("Application process paused for review. Check the Playwright window.")
            except Exception as e:
                st.error(f"Error during application: {e}")
        else:
            st.warning("Please enter a valid URL.")

st.divider()

# Bulk Apply Section
st.subheader("Bulk Apply to Saved Jobs")
apps = get_user_applications(st.session_state.user_id)
saved_apps = [app for app in apps if app['status'] == 'Saved']

if not saved_apps:
    st.info("No saved jobs found. Head to the Discovery tab to save jobs from the global pool.")
else:
    st.warning(f"You have **{len(saved_apps)}** jobs queued. Bulk Mode will execute applications rapidly in the background.")
    
    if st.button(f"🚀 Execute Bulk Apply ({len(saved_apps)} jobs)", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, app in enumerate(saved_apps):
            status_text.text(f"Applying to: {app['title']} ({i+1}/{len(saved_apps)})")
            try:
                apply_to_job(app['url'], user_profile, bulk_mode=True)
                update_user_job_status(app['uj_id'], "Applied")
            except Exception as e:
                st.error(f"Failed {app['title']}: {e}")
                
            progress_bar.progress((i + 1) / len(saved_apps))
            time.sleep(2) # Prevent rate limiting
            
        status_text.text("✅ Bulk Execution Complete!")
        st.balloons()
        
    st.write("---")
    st.write("**Queue:**")
    for app in saved_apps:
        st.markdown(f"- {app['title']} at {app['company']} ([Link]({app['url']}))")
