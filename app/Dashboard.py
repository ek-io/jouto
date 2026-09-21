import streamlit as st
import os
import sys
import pandas as pd

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import initialize_db, get_applications

st.set_page_config(
    page_title="AutoApply Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
initialize_db()

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# API Key Config (Hidden in sidebar)
if "GEMINI_API_KEY" in os.environ:
    st.sidebar.success("✅ AI Engine Active")
else:
    api_key = st.sidebar.text_input("Gemini API Key (Admin)", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    else:
        st.sidebar.warning("API Key missing. AI features disabled.")

# --- HERO SECTION ---
st.markdown("""
<div style="padding: 2rem 0; text-align: center;">
    <h1 style="color: #2557a7; font-size: 2.8rem; font-weight: 800; margin-bottom: 0;">Job Application Command Center</h1>
    <p style="color: #595959; font-size: 1.2rem; max-width: 600px; margin: 10px auto 30px auto;">
        Automate your job search, evaluate fit scores with AI, and track your pipeline all in one place.
    </p>
</div>
""", unsafe_allow_html=True)

# --- METRICS DASHBOARD ---
st.write("### 📈 Pipeline Overview")
apps = get_applications()

total_saved = len([a for a in apps if a['status'] == 'Saved'])
total_applied = len([a for a in apps if a['status'] == 'Applied'])
total_interviews = len([a for a in apps if a['status'] == 'Interviewing'])

# Calculate average fit score safely
scores = [a['fit_score'] for a in apps if a.get('fit_score')]
avg_score = int(sum(scores)/len(scores)) if scores else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Saved Opportunities", value=total_saved)
m2.metric(label="Applications Submitted", value=total_applied)
m3.metric(label="Active Interviews", value=total_interviews)
m4.metric(label="Avg. AI Fit Score", value=f"{avg_score}%")

st.divider()

# --- RECENT ACTIVITY ---
st.write("### 🕒 Recent Activity")

if not apps:
    st.info("Your pipeline is empty. Head over to the **Discovery** tab to find new roles!")
else:
    # Display the 5 most recent jobs in a clean table
    recent_apps = apps[:5]
    df = pd.DataFrame(recent_apps)
    
    # Format the dataframe for display
    display_df = df[['title', 'status', 'fit_score', 'applied_date']].copy()
    display_df.columns = ['Job Title', 'Status', 'Fit Score', 'Date Added']
    
    # Remove time from date
    display_df['Date Added'] = display_df['Date Added'].apply(lambda x: x[:10])
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

