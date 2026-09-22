import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.discovery import load_config, discover_jobs
from core.evaluator import evaluate_job, generate_cover_letter
from core.database import add_application
from app.components.ui_cards import render_job_card

st.set_page_config(page_title="Job Discovery", page_icon="🔍", layout="wide")

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔍 Job Discovery")

col1, col2 = st.columns([1, 4])
with col1:
    st.write("### Actions")
    
    with st.expander("📥 Bulk URL Importer"):
        st.write("Paste a list of job URLs (one per line) from external sources.")
        bulk_urls = st.text_area("Job URLs")
        if st.button("Import URLs to Database", use_container_width=True):
            urls = [u.strip() for u in bulk_urls.split('\n') if u.strip().startswith('http')]
            if urls:
                for url in urls:
                    add_application(title="Imported Job", url=url, snippet="Bulk imported URL.", fit_score=0)
                st.success(f"Imported {len(urls)} jobs to your history!")
            else:
                st.error("No valid URLs found.")
                
    st.divider()
    if st.button("Scrape Web Jobs", type="primary", use_container_width=True):
        with st.spinner("Scraping job boards via DuckDuckGo..."):
            config = load_config()
            titles = config.get("target_titles", [])
            jobs = discover_jobs(titles)
            
            if jobs:
                st.session_state.jobs = jobs
                st.success(f"Found {len(jobs)} jobs!")
            else:
                st.warning("No jobs found.")
    
    if "jobs" in st.session_state and st.button("Evaluate with AI", use_container_width=True):
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("Missing Gemini API Key!")
        else:
            with st.spinner("Evaluating fit scores..."):
                config = load_config()
                for job in st.session_state.jobs:
                    if 'fit_score' not in job:
                        evaluation = evaluate_job(job['snippet'], job['title'], config)
                        job['fit_score'] = evaluation.get('score', 0)
                        job['reasoning'] = evaluation.get('reasoning', '')
            st.success("Evaluation complete!")

with col2:
    if "jobs" in st.session_state:
        st.write(f"### Results ({len(st.session_state.jobs)})")
        
        # Sort by score descending if available
        sorted_jobs = sorted(st.session_state.jobs, key=lambda x: x.get('fit_score', 0), reverse=True)
        
        for idx, job in enumerate(sorted_jobs):
            render_job_card(job)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save to History", key=f"save_{idx}"):
                    add_application(
                        title=job.get('title'),
                        url=job.get('url'),
                        snippet=job.get('snippet'),
                        fit_score=job.get('fit_score', 0)
                    )
                    st.toast(f"Saved {job.get('title')} to History!")
            with c2:
                if st.button("Generate Cover Letter", key=f"cl_{idx}"):
                    if not os.environ.get("GEMINI_API_KEY"):
                        st.error("Missing Gemini API Key!")
                    else:
                        with st.spinner("Writing cover letter..."):
                            cl = generate_cover_letter(job['snippet'], job['title'], load_config())
                            st.text_area("Cover Letter", cl, height=300)
