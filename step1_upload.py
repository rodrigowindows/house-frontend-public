import streamlit as st
import pandas as pd
import requests
import json
import time
import tempfile
import os
from utils import navigation_buttons

def get_sample_data():
    """Return sample property data for testing."""
    return pd.DataFrame({
        "Account Number": ["TEST-00-00-0000-00000"],
        "Account Status": ["Unpaid"],
        "Owner Name": ["Test Owner"],
        "Property Address": ["123 Test Street, Test City, FL 12345"],
        "Balance Amount": [1000.00],
        "Assessed Value": [100000],
        "Tax Yr": [2023],
        "Roll Yr": [2023],
        "Cert Status": ["Pending"],
        "Deed Status": ["-- None --"],
        "Alternate Key": [12345]
    })

def process_files(file1, file2):
    """Process files using the API."""
    API_ENDPOINT = "https://llmmsi.a.pinggy.link/pc-house-automation/check_new_rows"
    
    try:
        with st.spinner("Calling API to process files..."):
            # Prepare files for upload
            files = {
                'file1': file1,
                'file2': file2
            }
            
            # Make API request
            response = requests.post(API_ENDPOINT, files=files)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Log response for debugging
                st.write(f"Received {data['count']} records from API")
                
                # Set session state with JSON data from response
                st.session_state.data = pd.DataFrame(data['json'])
                st.session_state.raw_csv = data['csv']
                
                st.success(f"Successfully processed {data['count']} property records!")
                time.sleep(1)
                st.session_state.step = 2
                st.rerun()
                return True
            else:
                st.error(f"API Error: Status code {response.status_code}")
                st.error(f"Response: {response.text}")
                return False
                
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return False

def process_direct_diff(diff_file):
    """Process the differences file directly for scraping."""
    try:
        with st.spinner("Processing differences file..."):
            # Read the CSV
            df = pd.read_csv(diff_file)
            
            # Set the data in session state
            st.session_state.data = df
            
            # Display a success message
            st.success(f"Successfully loaded {len(df)} records from differences file!")
            
            # Option to proceed directly to scraping
            cols = st.columns([3, 3])
            with cols[0]:
                if st.button("Continue to Review (Step 2)"):
                    st.session_state.step = 2
                    st.rerun()
            with cols[1]:
                if st.button("Skip to Scraping (Step 3)", type="primary"):
                    st.session_state.step = 3
                    st.rerun()
                    
            return True
    except Exception as e:
        st.error(f"Error processing differences file: {str(e)}")
        return False

def manual_data_entry():
    """Provide a form for manual data entry."""
    st.write("Add property information manually:")
    
    with st.form("manual_data_form"):
        cols1 = st.columns(3)
        with cols1[0]:
            acct_num = st.text_input("Account Number")
        with cols1[1]:
            owner_name = st.text_input("Owner Name")
        with cols1[2]:
            status = st.selectbox("Account Status", ["Unpaid", "Paid", "Pending"])
        
        cols2 = st.columns(2)
        with cols2[0]:
            property_address = st.text_input("Property Address")
        with cols2[1]:
            owner_address = st.text_input("Owner Address")
            
        cols3 = st.columns(3)
        with cols3[0]:
            balance = st.number_input("Balance Amount", min_value=0.0, step=100.0)
        with cols3[1]:
            assessed_value = st.number_input("Assessed Value", min_value=0, step=10000)
        with cols3[2]:
            alternate_key = st.number_input("Alternate Key", min_value=0, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            add_another = st.checkbox("Add multiple entries", value=False)
        
        submitted = st.form_submit_button("Add Data")
        
        if submitted:
            # Create dataframe with manual entry
            manual_df = pd.DataFrame([{
                "Account Number": acct_num if acct_num else "00-00-00-0000-00000",
                "Account Status": status,
                "Alternate Key": alternate_key,
                "Assessed Value": assessed_value,
                "Balance Amount": balance,
                "Property Address": property_address if property_address else "Unknown Address",
                "Owner Name": owner_name if owner_name else "New Owner",
                "Owner Address": owner_address if owner_address else "Unknown Owner Address",
                "Tax Yr": 2023,
                "Roll Yr": 2023,
                "Cert Status": "Pending",
                "Deed Status": "-- None --"
            }])
            
            st.session_state.data = manual_df
            st.success("Manual data added!")
            
            if not add_another:
                time.sleep(1)
                st.session_state.step = 2
                st.rerun()
            
    return st.session_state.data is not None

def upload_differences_file():
    """Provide direct differences file upload functionality."""
    st.subheader("Upload Differences File Directly")
    
    st.markdown("""
    Upload a single CSV file containing the differences data for direct scraping.
    This allows you to skip the standard two-file comparison process.
    """)
    
    # File uploader for differences file
    diff_file = st.file_uploader("Differences data file", type=['csv'], key="diff_file_uploader")
    
    if diff_file:
        st.success("Differences file uploaded!")
        
        # Preview button
        if st.button("Preview Differences File"):
            # Read and display a preview
            df = pd.read_csv(diff_file)
            st.write("Preview of first 5 rows:")
            st.dataframe(df.head(5), use_container_width=True)
        
        # Process button enabled when file is uploaded
        process_button = st.button("Process Differences File", type="primary")
        
        if process_button:
            return process_direct_diff(diff_file)
    
    return False

def csv_upload():
    """Provide standard CSV upload functionality with two files."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload First CSV")
        file1 = st.file_uploader("Tax certificate data file", type=['csv'])
        if file1:
            st.success("First CSV uploaded!")
            
    with col2:
        st.subheader("Upload Second CSV")
        file2 = st.file_uploader("Property data file", type=['csv'])
        if file2:
            st.success("Second CSV uploaded!")
    
    # Process button enabled only when files are uploaded
    process_button = st.button("Process Files", disabled=(not file1 or not file2))
    
    if process_button:
        return process_files(file1, file2)
    
    return False

def show():
    """Display the upload CSV step."""
    # Add quick navigation button at the top
    with st.sidebar:
        st.title("Fast Testing")
        if st.button("📱 Fast Forward to Page 5", use_container_width=True, type="primary"):
            # Initialize needed data for step 5
            st.session_state.step = 5
            
            # Set sample data for each step
            st.session_state.data = get_sample_data()
            
            # Import the function from step5_notify if available
            try:
                from step5_notify import get_sample_scraped_data
                st.session_state.final_data = get_sample_scraped_data()
            except ImportError:
                # Create sample scraped data directly
                st.session_state.final_data = pd.DataFrame({
                    "id": ["TEST-00-00-0000-00000", "TEST-00-00-0000-00000"],
                    "address": ["123 Test Street, Test City, FL 12345"] * 2,
                    "current_address": ["123 Test Street, Test City, FL 12345"] * 2,
                    "name": ["Test Owner"] * 2,
                    "type": ["phone_number", "email"],
                    "value": ["(111) 111-1111", "test@test.com"],
                    "selected": [True, True]
                })
            
            # Force rerun to refresh
            st.rerun()
            
    st.header("Step 1: Upload CSV Files")
    
    # Highlight the direct upload option
    st.markdown("""
    <div style="background-color: #f0f7fb; padding: 15px; border-radius: 5px; border-left: 5px solid #2196F3; margin-bottom: 20px;">
      <h3 style="color: #0d47a1; margin-top: 0;">NEW! Direct Differences Upload</h3>
      <p>You can now upload a differences file directly to skip the comparison process and proceed to scraping.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different data input methods
    tab1, tab2, tab3 = st.tabs(["Direct Differences Upload", "Standard CSV Upload", "Manual Entry"])
    
    with tab1:
        upload_differences_file()
    
    with tab2:
        st.markdown("""
        ### Upload property tax certificate files
        
        Upload the required files to start the workflow:
        - First file should contain tax certificate data
        - Second file should contain property data
        """)
        csv_upload()
    
    with tab3:
        manual_data_entry()
    
    # Navigation - only forward since we're on step 1
    st.markdown("---")
    navigation_buttons(back=False, next=True, next_label="Skip to Review Step ➡️", 
                      next_disabled=not (st.session_state.data is not None and not st.session_state.data.empty))