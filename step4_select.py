import streamlit as st
import pandas as pd
from utils import navigation_buttons
import step1_upload
import step3_scrape

def parse_uploaded_contacts(file):
    """Parse an uploaded contacts CSV file."""
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Check for required columns
        required_columns = ['id', 'name', 'type', 'value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            st.info("Your CSV file must include at minimum: 'id', 'name', 'type', and 'value' columns.")
            return None
        
        # Validate 'type' values
        valid_types = ['phone_number', 'email']
        invalid_types = df[~df['type'].isin(valid_types)]['type'].unique()
        
        if len(invalid_types) > 0:
            st.warning(f"Found invalid contact types: {', '.join(invalid_types)}. Only 'phone_number' and 'email' are valid.")
            # Fix by setting invalid types to 'phone_number'
            df.loc[~df['type'].isin(valid_types), 'type'] = 'phone_number'
            st.info("Invalid types have been converted to 'phone_number'.")
        
        # Add required columns if they don't exist
        if 'selected' not in df.columns:
            df['selected'] = True
        
        if 'address' not in df.columns:
            df['address'] = "Unknown Address"
            
        if 'current_address' not in df.columns:
            df['current_address'] = df['address']
        
        return df
        
    except Exception as e:
        st.error(f"Error parsing contacts file: {str(e)}")
        return None

def show():
    """Display the contact selection step."""
    st.header("Step 4: Review and Select Contact Information")
    
    # Add tab for manual upload - make tabs more prominent
    col1, col2 = st.columns(2)
    with col1:
        scraped_tab = st.button("Scraped Contacts", use_container_width=True, type="primary" if not "active_tab" in st.session_state or st.session_state.active_tab == "scraped" else "secondary")
    with col2:
        upload_tab = st.button("Upload Contact List", use_container_width=True, type="primary" if "active_tab" in st.session_state and st.session_state.active_tab == "upload" else "secondary")
    
    # Set active tab based on button clicks
    if scraped_tab:
        st.session_state.active_tab = "scraped"
    elif upload_tab:
        st.session_state.active_tab = "upload"
    
    # Initialize active tab if not set
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "scraped"
    
    # Show active tab content
    if st.session_state.active_tab == "scraped":
        # Initialize data if needed
        if not hasattr(st.session_state, 'data') or st.session_state.data is None:
            st.session_state.data = step1_upload.get_sample_data()
            st.warning("Using sample property data since no data was provided in previous steps.")
        
        if not hasattr(st.session_state, 'scraped_data') or st.session_state.scraped_data is None:
            st.session_state.scraped_data = step3_scrape.get_sample_scraped_data()
            st.warning("Using sample contact data since no scraping was performed.")
        
        # Display original property data
        with st.expander("Property Data"):
            if hasattr(st.session_state, 'selected_data') and st.session_state.selected_data is not None:
                original_data = st.session_state.selected_data
            else:
                original_data = st.session_state.data
                
            st.dataframe(original_data, use_container_width=True)
        
        # Group contact data by owner and type for better organization
        contact_data = st.session_state.scraped_data.copy()
        
        # Add a selection column if it doesn't exist
        if "selected" not in contact_data.columns:
            contact_data["selected"] = True
        
        # Group contacts by owner and display in expandable sections
        st.subheader("Available Contact Information")
        
        # Get unique property IDs and owners
        unique_properties = contact_data[["id", "name", "address"]].drop_duplicates()
        
        # Create a container for each property owner
        for _, prop in unique_properties.iterrows():
            property_id = prop["id"]
            owner_name = prop["name"]
            property_address = prop["address"]
            
            # Create an expander for each property/owner
            with st.expander(f"{owner_name} - {property_address} (ID: {property_id})"):
                # Filter contacts for this owner
                owner_contacts = contact_data[(contact_data["id"] == property_id) & 
                                            (contact_data["name"] == owner_name)]
                
                # Create tabs for phone numbers and emails
                tab1, tab2 = st.tabs(["Phone Numbers", "Email Addresses"])
                
                with tab1:
                    phone_contacts = owner_contacts[owner_contacts["type"] == "phone_number"]
                    if not phone_contacts.empty:
                        # Create a dataframe editor for phone numbers
                        phone_editor = st.data_editor(
                            phone_contacts,
                            column_config={
                                "selected": st.column_config.CheckboxColumn("Select", default=True),
                                "value": st.column_config.TextColumn("Phone Number", help="Owner's phone number"),
                                "name": st.column_config.TextColumn("Name", disabled=True),
                                "current_address": st.column_config.TextColumn("Current Address", help="Current address if different from property")
                            },
                            hide_index=True,
                            use_container_width=True,
                            disabled=["id", "address", "name", "type"]
                        )
                        
                        # Update the selection status in the main dataframe
                        for i, row in phone_editor.iterrows():
                            idx = contact_data[(contact_data["id"] == row["id"]) & 
                                            (contact_data["name"] == row["name"]) & 
                                            (contact_data["type"] == "phone_number") & 
                                            (contact_data["value"] == row["value"])].index
                            if len(idx) > 0:
                                contact_data.loc[idx, "selected"] = row["selected"]
                    else:
                        st.info("No phone numbers found for this owner.")
                
                elif st.session_state.active_tab == "upload":
                    email_contacts = owner_contacts[owner_contacts["type"] == "email"]
                    if not email_contacts.empty:
                        # Create a dataframe editor for emails
                        email_editor = st.data_editor(
                            email_contacts,
                            column_config={
                                "selected": st.column_config.CheckboxColumn("Select", default=True),
                                "value": st.column_config.TextColumn("Email Address", help="Owner's email address"),
                                "name": st.column_config.TextColumn("Name", disabled=True),
                                "current_address": st.column_config.TextColumn("Current Address", help="Current address if different from property")
                            },
                            hide_index=True,
                            use_container_width=True,
                            disabled=["id", "address", "name", "type"]
                        )
                        
                        # Update the selection status in the main dataframe
                        for i, row in email_editor.iterrows():
                            idx = contact_data[(contact_data["id"] == row["id"]) & 
                                            (contact_data["name"] == row["name"]) & 
                                            (contact_data["type"] == "email") & 
                                            (contact_data["value"] == row["value"])].index
                            if len(idx) > 0:
                                contact_data.loc[idx, "selected"] = row["selected"]
                    else:
                        st.info("No email addresses found for this owner.")
        
        # Save the updated contact data
        st.session_state.final_data = contact_data[contact_data["selected"] == True]
        
        # Manual contact entry option
        with st.expander("Add Contact Information Manually"):
            with st.form("add_manual_contact_data"):
                st.write("Add a new contact record:")
                
                cols1 = st.columns(3)
                with cols1[0]:
                    owner_name = st.text_input("Owner Name")
                with cols1[1]:
                    property_id = st.text_input("Property ID")
                with cols1[2]:
                    contact_type = st.selectbox("Contact Type", ["phone_number", "email"])
                
                cols2 = st.columns(2)
                with cols2[0]:
                    property_address = st.text_input("Property Address")
                with cols2[1]:
                    current_address = st.text_input("Current Address")
                    
                contact_value = st.text_input("Contact Value (Phone/Email)")
                
                submitted = st.form_submit_button("Add Contact")
                
                if submitted and contact_value:
                    # Create new record
                    new_record = pd.DataFrame({
                        "id": [property_id if property_id else "1"],
                        "address": [property_address if property_address else "Unknown Address"],
                        "current_address": [current_address if current_address else property_address],
                        "name": [owner_name if owner_name else "Unknown Owner"],
                        "type": [contact_type],
                        "value": [contact_value],
                        "selected": [True]
                    })
                    
                    # Append to existing data
                    updated_data = pd.concat([contact_data, new_record], ignore_index=True)
                    st.session_state.scraped_data = updated_data
                    st.success("Contact record added successfully!")
                    st.experimental_rerun()
    
    with tab2:
        st.subheader("Upload Contact List")
        
        # Information about expected format
        st.markdown("""
        ### CSV Format Instructions
        
        Upload a CSV file with your contact list. The file must contain at minimum these columns:
        
        - **id**: Property or account identifier
        - **name**: Contact name/owner name
        - **type**: Must be either 'phone_number' or 'email'
        - **value**: The actual phone number or email address
        
        Optional columns that will be used if present:
        - **address**: Property address
        - **current_address**: Current mailing address if different
        - **selected**: True/False to pre-select contacts
        
        Example CSV structure:
        ```
        id,name,type,value,address,current_address
        PROP-001,John Smith,phone_number,(555) 123-4567,123 Main St,123 Main St
        PROP-001,John Smith,email,john@example.com,123 Main St,123 Main St
        PROP-002,Jane Doe,phone_number,(555) 987-6543,456 Oak Ave,456 Oak Ave
        ```
        """)
        
        # Upload area
        uploaded_file = st.file_uploader("Upload Contact CSV", type="csv", key="contact_csv_uploader")
        
        if uploaded_file is not None:
            # Display preview button
            if st.button("Preview CSV"):
                try:
                    # Read the file for preview
                    preview_df = pd.read_csv(uploaded_file)
                    st.write("Preview of first 5 rows:")
                    st.dataframe(preview_df.head(5), use_container_width=True)
                    
                    # Reset the file pointer for later processing
                    uploaded_file.seek(0)
                except Exception as e:
                    st.error(f"Error previewing file: {str(e)}")
            
            # Process button
            if st.button("Process Contact List", type="primary"):
                # Parse the uploaded file
                contact_df = parse_uploaded_contacts(uploaded_file)
                
                if contact_df is not None:
                    # Save to session state
                    st.session_state.scraped_data = contact_df
                    st.session_state.final_data = contact_df[contact_df["selected"] == True]
                    
                    # Success message
                    st.success(f"Successfully loaded {len(contact_df)} contacts for {contact_df['name'].nunique()} unique owners!")
                    
                    # Display loaded data
                    st.subheader("Loaded Contact Data")
                    st.dataframe(contact_df, use_container_width=True)
                    
                    # Stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        unique_owners = contact_df['name'].nunique()
                        st.metric("Unique Owners", unique_owners)
                    with col2:
                        phone_count = contact_df[contact_df['type'] == 'phone_number'].shape[0]
                        st.metric("Phone Numbers", phone_count)
                    with col3:
                        email_count = contact_df[contact_df['type'] == 'email'].shape[0]
                        st.metric("Email Addresses", email_count)
        
        # Template download option
        st.markdown("### Download Template")
        st.write("You can download a template CSV file to fill in with your contacts:")
        
        # Create a simple template CSV
        template_data = pd.DataFrame({
            "id": ["PROP-001", "PROP-001", "PROP-002"],
            "name": ["Owner Name", "Owner Name", "Another Owner"],
            "type": ["phone_number", "email", "phone_number"],
            "value": ["(555) 123-4567", "email@example.com", "(555) 987-6543"],
            "address": ["123 Main St, City, State", "123 Main St, City, State", "456 Oak Ave, City, State"],
            "current_address": ["123 Main St, City, State", "123 Main St, City, State", "PO Box 789, City, State"],
            "selected": [True, True, True]
        })
        
        # Create CSV for download
        csv = template_data.to_csv(index=False)
        st.download_button(
            label="Download Template CSV",
            data=csv,
            file_name="contact_list_template.csv",
            mime="text/csv"
        )
    
    # Show preview of selected contact information
    st.subheader("Selected Contact Information Preview")
    if hasattr(st.session_state, 'final_data') and not st.session_state.final_data.empty:
        selected_data = st.session_state.final_data.copy()
        
        # Remove the selected column for display
        if "selected" in selected_data.columns:
            selected_data = selected_data.drop("selected", axis=1)
            
        st.dataframe(selected_data, use_container_width=True)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            unique_owners = selected_data['name'].nunique()
            st.metric("Unique Owners", unique_owners)
        with col2:
            phone_count = selected_data[selected_data['type'] == 'phone_number'].shape[0]
            st.metric("Phone Numbers", phone_count)
        with col3:
            email_count = selected_data[selected_data['type'] == 'email'].shape[0]
            st.metric("Email Addresses", email_count)
    else:
        st.warning("No contact information selected. Please select at least one contact to proceed.")
    
    # Navigation buttons
    st.markdown("---")
    navigation_buttons(back_label="⬅️ Back to Contact Scraping", next_label="Proceed to Send Notifications ➡️")