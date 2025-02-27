import streamlit as st
import pandas as pd
from utils import navigation_buttons
import step1_upload
import step3_scrape

def show():
    """Display the contact selection step."""
    st.header("Step 4: Review and Select Contact Information")
    
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
            
            with tab2:
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
    
    # Show preview of selected contact information
    st.subheader("Selected Contact Information Preview")
    if not st.session_state.final_data.empty:
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