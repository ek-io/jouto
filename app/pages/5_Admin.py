import streamlit as st
import pandas as pd
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_global_jobs, get_connection
import psycopg2.extras

st.set_page_config(page_title="Jouto | Admin", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

# --- ADMIN SECURITY CHECK ---
if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.warning("Please log in on the Dashboard first.")
    st.stop()

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
    
    # Fetch all columns including snippet for filtering
    c.execute("SELECT title, company, url, snippet, source, discovered_date FROM jobs ORDER BY discovered_date DESC LIMIT 5000")
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
    
    # --- FILTERS ---
    st.subheader("Data Export & Filtering")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        unique_sources = ["All"] + list(df['source'].unique())
        selected_source = st.selectbox("Filter by Source:", unique_sources)
    with c2:
        company_filter = st.text_input("Filter by Company:", placeholder="e.g. Google")
    with c3:
        keyword_filter = st.text_input("Deep Keyword Search (State/Salary/Requirements):", placeholder="e.g. California, $120k, Python")
        
    # Apply Filters
    filtered_df = df.copy()
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    if company_filter:
        filtered_df = filtered_df[filtered_df['company'].str.contains(company_filter, case=False, na=False)]
    if keyword_filter:
        # Search across title and snippet
        mask = filtered_df['title'].str.contains(keyword_filter, case=False, na=False) | \
               filtered_df['snippet'].str.contains(keyword_filter, case=False, na=False)
        filtered_df = filtered_df[mask]
        
    # --- EXCEL EXPORT ---
    def convert_df_to_excel(df_to_export):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_export.to_excel(writer, index=False, sheet_name='Jouto_Jobs')
        return output.getvalue()

    st.write(f"Showing **{len(filtered_df)}** matching jobs.")
    
    excel_data = convert_df_to_excel(filtered_df)
    st.download_button(
        label="📥 Export Current View to Excel (.xlsx)",
        data=excel_data,
        file_name="Jouto_Crawler_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
    
    st.divider()

    # --- DATAFRAME VIEW ---
    st.subheader("Raw Crawler Data")
    
    # Drop snippet from UI for cleaner view
    display_df = filtered_df.drop(columns=['snippet'])
    
    st.dataframe(
        display_df,
        column_config={
            "url": st.column_config.LinkColumn("Application Link"),
            "discovered_date": st.column_config.DatetimeColumn("Crawled At", format="D MMM YYYY, h:mm a")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("The global database is currently empty. The crawler may still be booting up.")
