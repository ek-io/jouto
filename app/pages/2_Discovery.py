import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_global_jobs, save_job_for_user, get_user_profile, add_global_job
from core.evaluator import evaluate_job

st.set_page_config(page_title="Job Discovery", page_icon="🔍", layout="wide")

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔍 Job Discovery Pool")
st.write("Browse the centralized global pool of scraped jobs. Evaluate them against your profile and save them to your personal queue.")

col1, col2 = st.columns([1, 4])
with col1:
    st.write("### Actions")
    if st.button("Refresh Job Pool", use_container_width=True):
        st.rerun()
        
    with st.expander("📥 Submit Jobs to Pool"):
        st.write("Paste a list of job URLs to add to the global pool.")
        bulk_urls = st.text_area("Job URLs")
        if st.button("Import URLs", use_container_width=True):
            urls = [u.strip() for u in bulk_urls.split('\n') if u.strip().startswith('http')]
            if urls:
                for url in urls:
                    add_global_job(title="Imported Job", url=url, source="User Import")
                st.success(f"Added {len(urls)} jobs to the pool!")
                st.rerun()
            else:
                st.error("No valid URLs found.")

with col2:
    st.write("### Global Job Pool")
    jobs = get_global_jobs(limit=50)
    
    if not jobs:
        st.info("The global job pool is empty. The crawler will populate it soon.")
    else:
        user_profile, _ = get_user_profile(st.session_state.user_id)
        
        for job in jobs:
            st.markdown(f"#### {job['title']} at {job['company']}")
            st.write(job['snippet'] or job['url'])
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Evaluate Fit", key=f"eval_{job['id']}"):
                    if not os.environ.get("GEMINI_API_KEY"):
                        st.error("Missing Gemini API Key!")
                    else:
                        with st.spinner("AI evaluating..."):
                            evaluation = evaluate_job(job['snippet'] or job['url'], job['title'], user_profile)
                            score = evaluation.get('score', 0)
                            reasoning = evaluation.get('reasoning', '')
                            
                            st.info(f"**Fit Score: {score}/100**\n\n{reasoning}")
                            save_job_for_user(st.session_state.user_id, job['id'], score, reasoning)
                            st.success("Saved to your queue!")
            with c2:
                if st.button("Save without AI", key=f"save_{job['id']}"):
                    save_job_for_user(st.session_state.user_id, job['id'], 0, "Manually saved")
                    st.success("Saved to your queue!")
            st.divider()
