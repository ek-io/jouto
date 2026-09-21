import streamlit as st

def render_job_card(job):
    score = job.get('fit_score', 0)
    badge_class = "badge-red"
    if score >= 80:
        badge_class = "badge-green"
    elif score >= 50:
        badge_class = "badge-yellow"
        
    html = f"""
    <div class="job-card">
        <div class="job-title" onclick="window.open('{job.get('url')}', '_blank')">{job.get('title', 'Unknown Title')}</div>
        <div class="job-company">Company Name Placeholder • Location Placeholder</div>
        
        <div style="margin-bottom: 12px;">
            <div class="badge {badge_class}">AI Fit Score: {score}/100</div>
            <div class="badge" style="background: #f3f2f1; color: #595959; border:none; border-radius: 4px;">Urgently Hiring</div>
        </div>
        
        <div class="job-snippet">{job.get('snippet', '')[:300]}...</div>
        
        <div style="margin-top: 16px; font-size: 0.85rem; color: #595959; background: #f8f9fa; padding: 10px; border-left: 3px solid #2557a7;">
            <strong>AI Reasoning:</strong> {job.get('reasoning', 'Not evaluated yet.')}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
