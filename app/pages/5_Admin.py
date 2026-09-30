import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_global_jobs, get_connection
import psycopg2.extras

st.set_page_config(page_title="Jouto | Admin", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

# --- ADMIN SECURITY CHECK ---
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()

# Replace this with your actual admin username(s)
ADMIN_USERNAMES = ["admin", "ek-io", "owner"]

if st.session_state.username.lower() not in ADMIN_USERNAMES:
    st.error("🛑 ACCESS DENIED. You do not have administrator privileges to view this page.")
    st.stop()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔐 Admin Control Panel")
st.write("Welcome, Admin. Here is the raw data inside the Supabase global crawler database.")

# --- FETCH ADMIN DATA ---
@st.cache_data(ttl=60)
def fetch_admin_job_stats():
    conn = get_connection()
    if not conn: return [], 0
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    c.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = c.fetchone()[0]
    
    c.execute("SELECT title, company, source, discovered_date, url FROM jobs ORDER BY discovered_date DESC LIMIT 1000")
    recent_jobs = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return recent_jobs, total_jobs

with st.spinner("Querying Supabase Postgres Engine..."):
    jobs_data, total_jobs = fetch_admin_job_stats()

# --- METRICS ---
if jobs_data:
    df = pd.DataFrame(jobs_data)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Jobs in Database", total_jobs)
    
    sources = df['source'].nunique() if 'source' in df.columns else 0
    m2.metric("Active Crawler Sources", sources)
    
    top_company = df['company'].mode()[0] if not df.empty else "N/A"
    m3.metric("Most Active Hiring Company", top_company)

    st.divider()

    st.subheader("Raw Crawler Data (Latest 1000 Jobs)")
    
    # Filter by source
    unique_sources = ["All"] + list(df['source'].unique())
    selected_source = st.selectbox("Filter by Crawler Source:", unique_sources)
    
    if selected_source != "All":
        df = df[df['source'] == selected_source]
        
    st.dataframe(
        df,
        column_config={
            "url": st.column_config.LinkColumn("Application Link"),
            "discovered_date": st.column_config.DatetimeColumn("Crawled At", format="D MMM YYYY, h:mm a")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("The global database is currently empty. The crawler may still be booting up.")
