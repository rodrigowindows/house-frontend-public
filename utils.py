import streamlit as st
import pandas as pd
import time
import requests

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "data" not in st.session_state:
        st.session_state.data = None
    if "scraped_data" not in st.session_state:
        st.session_state.scraped_data = None
    if "selected_data" not in st.session_state:
        st.session_state.selected_data = None
    if "notification_status" not in st.session_state:
        st.session_state.notification_status = None
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False
    if "show_sample_data" not in st.session_state:
        st.session_state.show_sample_data = False
    if "final_data" not in st.session_state:
        st.session_state.final_data = None
    if "raw_csv" not in st.session_state:
        st.session_state.raw_csv = None
    if "current_job" not in st.session_state:
        st.session_state.current_job = None
    if "column_order" not in st.session_state:
        st.session_state.column_order = None
    if "custom_column_order" not in st.session_state:
        st.session_state.custom_column_order = None

def show_progress_bar():
    """Display the progress bar and step indicators."""
    progress_container = st.container()
    with progress_container:
        steps = ["Upload CSVs", "Review & Edit", "Scrape Data", "Select Data", "Send Notifications"]
        progress_bar = st.progress((st.session_state.step - 1) / len(steps))
        cols = st.columns(len(steps))
        for i, step in enumerate(steps):
            with cols[i]:
                if st.session_state.step > i + 1:
                    st.markdown(f"✅ **{step}**")
                elif st.session_state.step == i + 1:
                    st.markdown(f"🔄 **{step}**")
                else:
                    st.markdown(f"⏳ {step}")

def call_api(endpoint, data=None, method="get"):
    """Make API calls to the real endpoints."""
    st.session_state.is_loading = True
    
    # Display a loading spinner
    with st.spinner(f"Processing request to {endpoint}..."):
        try:
            # API base URL (modify as needed)
            BASE_URL = "https://llmmsi.a.pinggy.link/pc-house-automation"
            
            if method.lower() == "get":
                response = requests.get(f"{BASE_URL}/{endpoint}")
            elif method.lower() == "post":
                response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check response
            if response.status_code in [200, 201, 202]:
                result = response.json()
                st.session_state.is_loading = False
                return result
            else:
                st.error(f"API Error: Status code {response.status_code}")
                st.session_state.is_loading = False
                return {"error": f"Status code {response.status_code}"}
        
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            st.session_state.is_loading = False
            return {"error": str(e)}

def next_step():
    """Go to the next step in the workflow."""
    st.session_state.step += 1
    st.rerun()

def previous_step():
    """Go to the previous step in the workflow."""
    st.session_state.step -= 1
    st.rerun()

def navigation_buttons(back=True, next=True, back_label="⬅️ Back", next_label="Next ➡️", next_disabled=False):
    """Create standard navigation buttons."""
    col1, col2 = st.columns(2)
    
    if back:
        with col1:
            if st.button(back_label):
                previous_step()
    
    if next:
        with col2:
            if st.button(next_label, disabled=next_disabled):
                next_step()