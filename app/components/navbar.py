import streamlit as st

def render_navbar():
    st.markdown("<h2 style='color: #2557a7; margin-bottom: 0; padding-bottom: 0;'>Jouto</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.page_link("Dashboard.py", label="Home", icon="🏠")
    with col2:
        st.page_link("pages/2_Discovery.py", label="Discovery", icon="🔍")
    with col3:
        st.page_link("pages/3_Auto_Apply.py", label="Auto Apply", icon="🚀")
    with col4:
        st.page_link("pages/4_History.py", label="History", icon="📊")
    with col5:
        st.page_link("pages/1_Profile.py", label="Profile", icon="👤")
        
    st.divider()
