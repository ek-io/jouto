import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.database import get_applications, update_status

st.set_page_config(page_title="Application History", page_icon="📊", layout="wide")

st.title("📊 Application History")

apps = get_applications()

if not apps:
    st.info("No applications in history yet.")
else:
    df = pd.DataFrame(apps)
    
    # Kanban Board View
    st.subheader("Kanban View")
    cols = st.columns(3)
    
    statuses = ["Saved", "Applied", "Interviewing"]
    
    for i, status in enumerate(statuses):
        with cols[i]:
            st.markdown(f"### {status}")
            status_apps = [a for a in apps if a['status'] == status]
            
            for app in status_apps:
                with st.container(border=True):
                    st.markdown(f"**{app['title']}**")
                    st.caption(f"Score: {app['fit_score']} | Date: {app['applied_date'][:10]}")
                    
                    new_status = st.selectbox(
                        "Move to", 
                        options=statuses, 
                        index=statuses.index(status),
                        key=f"status_{app['id']}"
                    )
                    if new_status != status:
                        update_status(app['id'], new_status)
                        st.rerun()

    st.divider()
    
    # Table View
    st.subheader("Table View")
    st.dataframe(
        df[['title', 'status', 'fit_score', 'applied_date', 'url']], 
        use_container_width=True,
        hide_index=True
    )
