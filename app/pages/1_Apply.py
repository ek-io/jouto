import streamlit as st
from PIL import Image
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import get_user_profile, search_global_jobs, save_user_job, update_user_job_status
from core.evaluator import evaluate_job
from core.applier import apply_to_job

st.set_page_config(page_title="Jouto | Bulk Apply", page_icon=Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if 'pages' in __file__ else os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.jpg')), layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Please log in from the Dashboard first.")
    st.stop()

st.title("🚀 1-Click Magic Apply")

user_profile, resume_name, resume_file = get_user_profile(st.session_state.user_id)
if not user_profile or not resume_file:
    st.warning("⚠️ Your profile or resume is missing. We need your details before we can auto-apply.")
    if st.button("Go to Profile Settings"):
        st.switch_page("pages/2_Profile.py")
    st.stop()

st.markdown("""
<div style="background-color: #e8f3fb; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h4>Profile Verified ✅</h4>
    <p>Your resume and skills are securely loaded. We are ready to launch.</p>
</div>
""", unsafe_allow_html=True)

target_role = st.text_input("🎯 What Job Role are you looking for?", placeholder="e.g., Software Engineer, Data Scientist")

if st.button("START ENGINE", type="primary", use_container_width=True):
    if not target_role:
        st.error("Please enter a target role.")
        st.stop()
        
    with st.spinner("Searching Global Database for matching jobs..."):
        time.sleep(1) # Visual effect
        # Simple text search on title
        matching_jobs = search_global_jobs(target_role)
    
    if not matching_jobs:
        st.error(f"No active jobs found matching '{target_role}'. Our crawler is constantly fetching new ones. Try again in an hour!")
        st.stop()
        
    st.success(f"Found {len(matching_jobs)} potential roles!")
    
    st.write("### 🧠 AI Evaluation & Auto-Apply")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    successful_applications = 0
    
    for i, job in enumerate(matching_jobs[:10]): # Limit to 10 for safety/time
        progress = (i) / min(len(matching_jobs), 10)
        progress_bar.progress(progress)
        
        status_text.text(f"Evaluating: {job['title']} at {job['company']}")
        
        # Evaluate Fit
        fit_result = evaluate_job(job['snippet'], job['title'], user_profile)
        score = fit_result.get('score', 0)
        
        if score >= 75:
            # Good fit! Save it and apply
            user_job_id = save_user_job(st.session_state.user_id, job['id'], score, "Auto-Applying")
            
            status_text.text(f"Applying: {job['title']} at {job['company']} (Score: {score}%)")
            
            # Trigger Playwright Engine
            user_profile['resume_file'] = resume_file
            user_profile['resume_name'] = resume_name
            success = apply_to_job(job['url'], user_profile, bulk_mode=True)
            
            if success:
                update_user_job_status(user_job_id, "Applied")
                successful_applications += 1
                st.write(f"✅ **Applied!** {job['title']} at {job['company']} (AI Score: {score}%)")
            else:
                update_user_job_status(user_job_id, "Failed")
                st.write(f"❌ **Failed:** Could not parse form for {job['title']} at {job['company']}")
        else:
            st.write(f"⏭️ Skipped: {job['title']} at {job['company']} (AI Score: {score}%) - Too low.")
            
    progress_bar.progress(1.0)
    status_text.text("Bulk Application Complete!")
    st.balloons()
    st.success(f"Successfully submitted {successful_applications} applications!")
