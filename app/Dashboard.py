import streamlit as st
from PIL import Image
import os
import sys
import pandas as pd

# Add parent directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import initialize_db, verify_user, create_user, get_user_applications

st.set_page_config(
    page_title="Jouto | Dashboard",
    page_icon=Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if 'pages' in __file__ else os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.jpg')),
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def run_init_db():
    initialize_db()

run_init_db()

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

import extra_streamlit_components as stx

if "cookie_manager" not in st.session_state:
    st.session_state.cookie_manager = stx.CookieManager()

cookie_manager = st.session_state.cookie_manager

# --- AUTHENTICATION GATE ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Check cookie on hard refresh
stored_uid = cookie_manager.get(cookie="jouto_user_id")
stored_uname = cookie_manager.get(cookie="jouto_username")

if stored_uid and stored_uname and st.session_state.user_id is None:
    st.session_state.user_id = int(stored_uid)
    st.session_state.username = stored_uname
    st.rerun()

if st.session_state.user_id is None:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #2557a7;'>Jouto</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Your Job Search Automated.</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio("Select Action", ["Login", "Sign Up"], horizontal=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Login":
            if st.button("Log In", use_container_width=True, type="primary"):
                uid = verify_user(username, password)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = username
                    # Set cookie for 30 days
                    cookie_manager.set("jouto_user_id", str(uid), key="set_uid")
                    cookie_manager.set("jouto_username", username, key="set_uname")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        else:
            if st.button("Create Account", use_container_width=True, type="primary"):
                if create_user(username, password):
                    st.success("Account created! Please log in.")
                else:
                    st.error("Username already exists.")
    st.stop() # Halt rendering until logged in

# --- AUTHENTICATED DASHBOARD ---

c1, c2 = st.columns([4, 1])
with c1:
    st.write(f"### Welcome back, {st.session_state.username}!")
with c2:
    if st.button("Log Out", use_container_width=True):
        st.session_state.user_id = None
        cookie_manager.delete("jouto_user_id")
        cookie_manager.delete("jouto_username")
        st.rerun()

# --- HERO SECTION ---
st.markdown("""
<div style="padding: 1rem 0; text-align: center;">
    <h1 style="color: #2557a7; font-size: 2.8rem; font-weight: 800; margin-bottom: 0;">1-Click Magic Apply</h1>
    <p style="color: #595959; font-size: 1.2rem; max-width: 600px; margin: 10px auto 30px auto;">
        Enter your target role and let our AI engine automatically evaluate, rank, and apply to hundreds of matching roles for you.
    </p>
</div>
""", unsafe_allow_html=True)

# BIG APPLY BUTTON
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 START BULK APPLY", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Apply.py")

st.divider()

# --- METRICS DASHBOARD ---
st.write("### 📈 Pipeline Overview")
apps = get_user_applications(st.session_state.user_id)

total_saved = len([a for a in apps if a['status'] == 'Saved'])
total_applied = len([a for a in apps if a['status'] == 'Applied'])
total_interviews = len([a for a in apps if a['status'] == 'Interviewing'])

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
    st.info("Your pipeline is empty. Click START BULK APPLY to begin!")
else:
    recent_apps = apps[:5]
    df = pd.DataFrame(recent_apps)
    
    display_df = df[['title', 'company', 'status', 'fit_score']].copy()
    display_df.columns = ['Job Title', 'Company', 'Status', 'Fit Score']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
