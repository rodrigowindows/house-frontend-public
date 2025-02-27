import streamlit as st
import time
from utils import initialize_session_state, call_api, show_progress_bar
import step1_upload
import step2_review
import step3_scrape
import step4_select
import step5_notify

# Page config
st.set_page_config(page_title="Sequential Workflow", layout="wide")
st.title("5-Step Sequential Workflow")

# Initialize session state
initialize_session_state()

# Show progress bar at the top
show_progress_bar()

st.markdown("---")

# Display the current step
if st.session_state.step == 1:
    step1_upload.show()
elif st.session_state.step == 2:
    step2_review.show()
elif st.session_state.step == 3:
    step3_scrape.show()
elif st.session_state.step == 4:
    step4_select.show()
elif st.session_state.step == 5:
    step5_notify.show()

# Add navigation sidebar
with st.sidebar:
    st.title("Workflow Navigation")
    st.markdown("---")
    
    # Display current step
    st.markdown(f"### Current Step: {st.session_state.step}/5")
    st.markdown("You can skip steps and add data manually at any point.")
    
    # Navigation buttons for direct access to steps
    if st.button("1. Upload CSVs"):
        st.session_state.step = 1
        st.experimental_rerun()
        
    if st.button("2. Review Data"):
        if st.session_state.data is None:
            st.session_state.data = step1_upload.get_sample_data()
        st.session_state.step = 2
        st.experimental_rerun()
        
    if st.button("3. Scrape Data"):
        if st.session_state.data is None:
            st.session_state.data = step1_upload.get_sample_data()
        st.session_state.step = 3
        st.experimental_rerun()
        
    if st.button("4. Select Data"):
        if st.session_state.data is None:
            st.session_state.data = step1_upload.get_sample_data()
        if st.session_state.scraped_data is None:
            st.session_state.scraped_data = step3_scrape.get_sample_scraped_data()
        st.session_state.step = 4
        st.experimental_rerun()
        
    if st.button("5. Send Notifications"):
        if st.session_state.data is None:
            st.session_state.data = step1_upload.get_sample_data()
        if not hasattr(st.session_state, 'final_data') or st.session_state.final_data is None:
            # Create sample final data if missing
            st.session_state.final_data = step1_upload.get_sample_data()
        st.session_state.step = 5
        st.experimental_rerun()
        
    st.markdown("---")
    
    # Help information
    with st.expander("Help & Information"):
        st.markdown("""
        **Skip & Manual Entry**:
        - You can skip steps using the sidebar navigation
        - Each skipped step will use sample data
        - Manual data entry is available at each step
        
        **Workflow Steps**:
        1. Upload CSV files or enter data manually
        2. Review and edit imported data
        3. Scrape additional data from external sources
        4. Select and combine data for notifications
        5. Configure and send notifications
        """)
    
    # Reset workflow
    if st.button("Reset Workflow"):
        for key in list(st.session_state.keys()):
            if key != "step":
                del st.session_state[key]
        st.session_state.step = 1
        initialize_session_state()
        st.experimental_rerun()