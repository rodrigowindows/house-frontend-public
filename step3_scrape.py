import streamlit as st
import pandas as pd
import requests
import time
import tempfile
import os

# API endpoints
API_BASE_URL = "http://llmmsi.a.pinggy.link/house-screenscraper/api"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"
JOB_STATUS_ENDPOINT = f"{API_BASE_URL}/job"
DOWNLOAD_ENDPOINT = f"{API_BASE_URL}/download"

def get_sample_scraped_data():
    """Return sample scraped data."""
    import pandas as pd
    
    # Create a sample DataFrame with contact information
    sample_data = pd.DataFrame({
        "id": ["TEST-00-00-0000-00000", "TEST-00-00-0000-00000", "TEST-00-00-0000-00000"],
        "address": ["123 Test Street, Test City, FL 12345"] * 3,
        "current_address": ["123 Test Street, Test City, FL 12345"] * 3,
        "name": ["Test Owner"] * 3,
        "type": ["phone_number", "phone_number", "email"],
        "value": ["(111) 111-1111", "(222) 222-2222", "test@test.com"],
        "selected": [True, True, True]
    })
    
    return sample_data

def check_job_status(job_id):
    """Check the status of a specific job."""
    try:
        response = requests.get(f"{JOB_STATUS_ENDPOINT}/{job_id}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error checking job status: {str(e)}")
        return None

def get_job_results(job_id):
    """Get the results of a completed job."""
    try:
        response = requests.get(f"{DOWNLOAD_ENDPOINT}/{job_id}/json")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error getting job results: {str(e)}")
        return None

def scraping_options():
    """Provide options for contact data scraping."""
    st.header("Step 3: Scrape Additional Property Data")
    
    # Handle data retrieval and continuation first for better flow
    # This comes first so it's visible at the top if job results are ready
    if 'job_results' in st.session_state and st.session_state.job_results is not None:
        st.subheader("🟢 JOB COMPLETED: Scraped Data Ready")
        
        # Create a highlighted section for the button
        st.markdown("---")
        
        # Create a colored box to make the button more visible
        st.markdown("""
        <div style="background-color: #e1f5fe; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: #0277bd; margin-top: 0;">Results Retrieved Successfully!</h3>
            <p>Your scraped data is ready. Click the button below to save and continue to the next step.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display results in a collapsible section
        with st.expander("View Scraped Data Results"):
            st.dataframe(st.session_state.job_results)
        
        # Make the button prominent and centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ SAVE SCRAPED DATA & CONTINUE TO STEP 4", type="primary", use_container_width=True):
                results_df = st.session_state.job_results
                
                # Save to session state
                st.session_state.scraped_data = results_df
                
                # Combine scraped data with original data if it exists
                if hasattr(st.session_state, 'data') and st.session_state.data is not None:
                    # Ensure unique identification
                    results_df['_source'] = 'scraped'
                    st.session_state.data['_source'] = 'original'
                    
                    # Merge based on common columns
                    merged_data = pd.concat([st.session_state.data, results_df], ignore_index=True)
                    st.session_state.data = merged_data
                
                st.success("Scraped data saved and merged!")
                st.session_state.step = 4  # Move to next step
                st.rerun()
        
        st.markdown("---")
    
    # Now continue with the rest of the UI for data selection and job management
    if hasattr(st.session_state, 'data') and st.session_state.data is not None:
        # Create a copy of the data for editing
        data_for_scraping = st.session_state.data.copy()
        
        # Prepare data editor configuration
        column_config = {}
        
        # Define column configurations based on data types
        for col in data_for_scraping.columns:
            if col in ['Account Number', 'Owner Name', 'Property Address', 'Owner Address', 'Billing Address', 'Cert Status', 'Deed Status', 'Millage Code']:
                column_config[col] = st.column_config.TextColumn(col)
            elif col in ['Balance Amount', 'Assessed Value']:
                column_config[col] = st.column_config.NumberColumn(
                    col, 
                    format="$%.2f",
                    min_value=0
                )
            elif col in ['Alternate Key', 'Bidder #', 'Cert #', 'Roll Yr', 'Tax Yr']:
                column_config[col] = st.column_config.NumberColumn(
                    col, 
                    format="%d"
                )
        
        # Explicitly add selection column
        data_for_scraping['_select'] = True
        column_config['_select'] = st.column_config.CheckboxColumn(
            "Scrape", 
            default=True
        )
        
        # Column Management Section
        st.subheader("Column Management")
        col_mgmt_tabs = st.tabs(["Add Column", "Remove Column", "Reorder Columns"])
        
        with col_mgmt_tabs[0]:
            # Add Column
            new_col_name = st.text_input("New Column Name")
            col_type = st.selectbox("Column Type", ["Text", "Number", "Checkbox"])
            
            if st.button("Add Column"):
                if new_col_name and new_col_name not in data_for_scraping.columns:
                    # Add column based on selected type
                    if col_type == "Text":
                        data_for_scraping[new_col_name] = ""
                        column_config[new_col_name] = st.column_config.TextColumn(new_col_name)
                    elif col_type == "Number":
                        data_for_scraping[new_col_name] = 0
                        column_config[new_col_name] = st.column_config.NumberColumn(new_col_name)
                    elif col_type == "Checkbox":
                        data_for_scraping[new_col_name] = False
                        column_config[new_col_name] = st.column_config.CheckboxColumn(new_col_name)
                    st.success(f"Column '{new_col_name}' added successfully!")
        
        with col_mgmt_tabs[1]:
            # Remove Column
            col_to_remove = st.selectbox("Select Column to Remove", 
                [col for col in data_for_scraping.columns if col not in ['_select']])
            
            if st.button("Remove Selected Column"):
                if col_to_remove and col_to_remove in data_for_scraping.columns:
                    data_for_scraping = data_for_scraping.drop(columns=[col_to_remove])
                    if col_to_remove in column_config:
                        del column_config[col_to_remove]
                    st.success(f"Column '{col_to_remove}' removed successfully!")
        
        with col_mgmt_tabs[2]:
            # Get current columns (excluding '_select')
            current_columns = [col for col in data_for_scraping.columns if col != '_select']
            
            # Create a form for column reordering
            st.write("Drag and drop columns to reorder")
            reordered_columns = st.multiselect(
                "Reorder Columns", 
                current_columns, 
                default=current_columns
            )
            
            # Add a submit button to save the order
            if st.button("Save Column Order"):
                # Store the column order in session state
                st.session_state.custom_column_order = reordered_columns
                st.success("Column order saved!")
        
        # Allow user to select rows for scraping
        st.subheader("Select and Edit Properties to Scrape")
        filtered_data = st.data_editor(
            data_for_scraping, 
            column_config=column_config,
            num_rows="dynamic",  # Allow adding/deleting rows
            hide_index=True
        )
        
        # Calculate selected rows
        selected_rows = filtered_data[filtered_data['_select'] == True]
        st.write(f"Selected {len(selected_rows)} out of {len(filtered_data)} properties")
        
        # Scraping button
        if st.button("Start Scraping Selected Properties"):
            with st.spinner("Initiating data scraping..."):
                # Prepare CSV from selected data
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                
                # Get the custom column order or use default
                current_columns = [col for col in data_for_scraping.columns if col != '_select']
                column_order = st.session_state.get('custom_column_order', current_columns)
                
                # Remove the selection column and get only selected rows
                scrape_df = selected_rows.copy()
                scrape_df = scrape_df.drop(columns=['_select'])
                
                # Validate and enforce column order - FIX HERE
                # Check if column_order is None or empty before iterating
                final_columns = []
                if column_order:  # Check if column_order exists and is not empty
                    for col in column_order:
                        if col in scrape_df.columns:
                            final_columns.append(col)
                
                # If no custom order is found, use original columns
                if not final_columns:
                    final_columns = [col for col in current_columns if col in scrape_df.columns]
                
                # Reorder columns
                scrape_df = scrape_df[final_columns]
                
                # Save to CSV
                scrape_df.to_csv(temp_file.name, index=False)
                temp_file.close()
                
                # Debug information
                st.write("Columns being scraped:", scrape_df.columns.tolist())
                
                try:
                    with open(temp_file.name, 'rb') as file:
                        # Prepare files for upload
                        files = {'file': file}
                        
                        # Make API request
                        response = requests.post(UPLOAD_ENDPOINT, files=files)
                        
                        # Check response
                        if response.status_code in [200, 202]:
                            result = response.json()
                            
                            # Store job information in session state
                            st.session_state.current_job = {
                                'job_id': result.get('job_id'),
                                'status': result.get('status'),
                                'message': result.get('message')
                            }
                            
                            # Display job information
                            st.subheader("Job Information")
                            st.json(st.session_state.current_job)
                        else:
                            st.error(f"API Error: {response.status_code}")
                            st.error(response.text)
                
                except Exception as e:
                    st.error(f"Error during scraping: {str(e)}")
                
                # Clean up temporary file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    else:
        st.warning("No property data available from previous steps.")
    
    # Job management section
    st.subheader("Job Management")
    
    # Check Job Status Button - add a check for current_job
    if hasattr(st.session_state, 'current_job') and st.session_state.current_job is not None:
        job_id = st.session_state.current_job.get('job_id')
        
        if job_id:
            # Show current job status
            st.info(f"Current Job ID: {job_id}")
            st.info(f"Status: {st.session_state.current_job.get('status', 'Unknown')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Check Job Status"):
                    # Fetch and display job status
                    status = check_job_status(job_id)
                    if status:
                        # Update the stored job information
                        st.session_state.current_job.update(status)
                        
                        # Display updated job information
                        st.subheader("Updated Job Status")
                        st.json(st.session_state.current_job)
            
            # Get Job Results Button (only if status is completed)
            with col2:
                if st.session_state.current_job.get('status') == 'completed':
                    if st.button("Get Job Results"):
                        # Fetch and display job results
                        results = get_job_results(job_id)
                        if results:
                            results_df = pd.DataFrame(results)
                            
                            # Save results to session state
                            st.session_state.job_results = results_df
                            
                            # Force a rerun to show the results and continue button at the top
                            st.rerun()
    
    # Manual override option
    with st.expander("Manual Override Options"):
        st.warning("Use these options only if you're experiencing issues with the standard flow.")
        
        if st.button("Use Sample Scraped Data"):
            sample_data = get_sample_scraped_data()
            st.session_state.scraped_data = sample_data
            st.success("Sample scraped data loaded")
            
            if st.button("Continue to Step 4 with Sample Data"):
                st.session_state.step = 4
                st.rerun()
        
        if hasattr(st.session_state, 'current_job') and st.session_state.current_job is not None:
            if st.button("Force Continue to Step 4"):
                # If we have job results, use them
                if 'job_results' in st.session_state and st.session_state.job_results is not None:
                    st.session_state.scraped_data = st.session_state.job_results
                # Otherwise use sample data
                else:
                    st.session_state.scraped_data = get_sample_scraped_data()
                
                st.session_state.step = 4
                st.rerun()
    
    return False

def show():
    """Display the contact scraping step."""
    # Ensure property data exists
    if not hasattr(st.session_state, 'data') or st.session_state.data is None:
        st.warning("No property data available from previous steps.")
        st.info("Please upload or manually enter property data first.")
        return
    
    scraping_options()
