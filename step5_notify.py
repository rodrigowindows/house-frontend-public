import streamlit as st
import pandas as pd
import time
import json
import requests
from utils import call_api, navigation_buttons

def get_sample_data():
    """Return sample property data."""
    import pandas as pd
    
    # Create a sample DataFrame with property information
    sample_data = pd.DataFrame({
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
    
    return sample_data

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

def select_first_contacts():
    """
    Select only the first phone number and first email for each property ID
    """
    if not hasattr(st.session_state, 'final_data') or st.session_state.final_data is None:
        return
        
    # Get the data
    contact_data = st.session_state.final_data.copy()
    
    # Filter to get unique IDs
    unique_ids = contact_data['id'].unique()
    
    # Create empty dataframe for selected contacts
    selected_contacts = pd.DataFrame()
    
    # For each unique ID, get the first phone number and first email
    for id_val in unique_ids:
        id_contacts = contact_data[contact_data['id'] == id_val]
        
        # Get first phone number
        phone_contacts = id_contacts[id_contacts['type'] == 'phone_number']
        if not phone_contacts.empty:
            selected_contacts = pd.concat([selected_contacts, phone_contacts.iloc[0:1]], ignore_index=True)
            
        # Get first email
        email_contacts = id_contacts[id_contacts['type'] == 'email']
        if not email_contacts.empty:
            selected_contacts = pd.concat([selected_contacts, email_contacts.iloc[0:1]], ignore_index=True)
    
    # Update all selected contacts to True for send_to
    if 'send_to' in selected_contacts.columns:
        selected_contacts['send_to'] = True
    else:
        selected_contacts['send_to'] = True
        
    # Update session state
    st.session_state.final_data = selected_contacts
    
    return selected_contacts

def send_marketing_notification(contact_dict):
    """Send notification via the marketing API."""
    try:
        # API endpoint
        API_ENDPOINT = "http://llmmsi.a.pinggy.link/marketing/start"
        
        # Extract contact information
        name = contact_dict["name"]
        address = contact_dict["address"]
        
        # Create payload
        payload = {
            "name": name,
            "address": address
        }
        
        # Get phone number and email for this contact
        phone_value = None
        email_value = None
        
        # Find phone number and email from the data
        if "phone_data" in contact_dict and contact_dict["phone_data"] is not None:
            phone_value = contact_dict["phone_data"]["value"]
            
        if "email_data" in contact_dict and contact_dict["email_data"] is not None:
            email_value = contact_dict["email_data"]["value"]
        
        # Add to payload if available
        if phone_value:
            payload["phone_number"] = phone_value
            
        if email_value:
            payload["email"] = email_value
        
        # Debug
        st.write(f"Sending payload: {payload}")
        
        # Send request
        response = requests.post(API_ENDPOINT, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        
        # Check response
        if response.status_code == 200:
            return response.json(), True
        else:
            st.error(f"API Error: {response.status_code}")
            st.error(f"Response: {response.text}")
            return response.text, False
            
    except Exception as e:
        st.error(f"Error sending notification: {str(e)}")
        return str(e), False

def show():
    """Display the notification step."""
    # Add quick navigation button at the top
    with st.sidebar:
        st.title("Fast Testing")
        if st.button("📱 Fast Forward to Page 5", use_container_width=True, type="primary"):
            # Initialize needed data for step 5
            st.session_state.step = 5
            
            # Set sample data for each step
            st.session_state.data = get_sample_data()
            st.session_state.final_data = get_sample_scraped_data()
            
            # Force rerun to refresh
            st.rerun()
    
    st.header("Step 5: Send Notifications")
    
    st.write("Configure and send notifications to property owners using selected contact information.")
    
    # Initialize data if needed
    if not hasattr(st.session_state, 'final_data') or st.session_state.final_data is None or st.session_state.final_data.empty:
        st.session_state.final_data = get_sample_scraped_data()
        st.warning("Using sample contact data since no contacts were selected in previous steps.")
    
    # First Contacts Only button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📞 Select First Contacts Only", help="For each property, select only the first phone number and first email"):
            selected = select_first_contacts()
            if selected is not None:
                st.success(f"Selected {len(selected)} contacts (first phone and email for each property)")
                st.rerun()
    
    # Group contacts by owner for better organization
    contact_data = st.session_state.final_data.copy()
    
    # Add send_to column if it doesn't exist
    if "send_to" not in contact_data.columns:
        contact_data["send_to"] = True
    
    # Display contacts grouped by owner
    st.subheader("Recipients")
    
    # Get unique owners
    unique_owners = contact_data[["id", "name", "address"]].drop_duplicates()
    owners_data = {}
    
    # Counter for unique widget keys
    widget_counter = 0
    
    for _, owner in unique_owners.iterrows():
        widget_counter += 1
        owner_id = owner["id"]
        owner_name = owner["name"]
        owner_address = owner["address"]
        
        # Using a unique expander key for each owner
        with st.expander(f"{owner_name} - {owner_address} (ID: {owner_id})", expanded=True):
            # Filter contacts for this owner
            owner_contacts = contact_data[(contact_data["id"] == owner_id) & 
                                        (contact_data["name"] == owner_name)]
            
            # Create a dataframe editor for this owner's contacts with a UNIQUE key
            # The key issue is here - we need to ensure each data_editor has a unique key
            unique_editor_key = f"editor_{owner_id}_{widget_counter}"
            
            edited_contacts = st.data_editor(
                owner_contacts,
                column_config={
                    "send_to": st.column_config.CheckboxColumn("Send", default=True),
                    "type": st.column_config.SelectboxColumn(
                        "Contact Type", 
                        help="Type of contact",
                        options=["phone_number", "email"],
                        disabled=True
                    ),
                    "value": st.column_config.TextColumn("Contact Value", help="Phone number or email address"),
                    "current_address": st.column_config.TextColumn("Current Address", help="Current address if different from property")
                },
                hide_index=True,
                use_container_width=True,
                disabled=["id", "address", "name", "type"],
                key=unique_editor_key  # Using the unique key here
            )
            
            # Store the edited data for this owner
            owners_data[owner_id] = edited_contacts
    
    # Combine all the edited data
    updated_contacts = pd.DataFrame()
    for owner_id, edited_data in owners_data.items():
        updated_contacts = pd.concat([updated_contacts, edited_data], ignore_index=True)
    
    # Update the session state with the edited data
    st.session_state.final_data = updated_contacts
    
    # Only include rows where send_to is True
    selected_contacts = updated_contacts[updated_contacts["send_to"] == True]
    if "send_to" in selected_contacts.columns:
        selected_contacts = selected_contacts.drop("send_to", axis=1)
    
    # Preview and send
    st.subheader("Review and Send")
    
    if len(selected_contacts) > 0:
        # Count by type
        phone_count = len(selected_contacts[selected_contacts["type"] == "phone_number"])
        email_count = len(selected_contacts[selected_contacts["type"] == "email"])
        
        # Display what will be sent
        st.write(f"You are about to send notifications to {len(selected_contacts['name'].unique())} property owners")
        st.write(f"• Phone numbers: {phone_count}")
        st.write(f"• Email addresses: {email_count}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Contact Selection"):
                st.session_state.step = 4
                st.rerun()
                
        with col2:
            send_button = st.button("Send Notifications", type="primary")
            
            if send_button and not selected_contacts.empty:
                # Call API to send notifications
                with st.spinner("Sending notifications..."):
                    # Group by property for API call
                    unique_ids = selected_contacts["id"].unique()
                    
                    # Prepare for status tracking
                    status_df = pd.DataFrame(columns=[
                        "id", "name", "contact", "type", "timestamp", "status", "response"
                    ])
                    
                    # Process each property one by one
                    for property_id in unique_ids:
                        # Get the property information
                        property_data = selected_contacts[selected_contacts["id"] == property_id].iloc[0]
                        
                        # Get the phone number and email for this property
                        phone_data = None
                        email_data = None
                        
                        # Get phone data if available
                        phone_rows = selected_contacts[(selected_contacts["id"] == property_id) & 
                                                    (selected_contacts["type"] == "phone_number")]
                        if not phone_rows.empty:
                            phone_data = phone_rows.iloc[0].to_dict()
                        
                        # Get email data if available
                        email_rows = selected_contacts[(selected_contacts["id"] == property_id) & 
                                                    (selected_contacts["type"] == "email")]
                        if not email_rows.empty:
                            email_data = email_rows.iloc[0].to_dict()
                        
                        # Create the contact dictionary
                        contact_dict = {
                            "id": property_id,
                            "name": property_data["name"],
                            "address": property_data["address"],
                            "phone_data": phone_data,
                            "email_data": email_data
                        }
                        
                        # Send notification
                        response, success = send_marketing_notification(contact_dict)
                        
                        # Record status
                        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Add phone status if available
                        if phone_data is not None:
                            phone_value = phone_data["value"]
                            status_df = pd.concat([status_df, pd.DataFrame([{
                                "id": property_id,
                                "name": property_data["name"],
                                "contact": phone_value,
                                "type": "Call/SMS",
                                "timestamp": timestamp,
                                "status": "Sent" if success else "Failed",
                                "response": str(response.get("call_status_code", "N/A")) if success else "Error"
                            }])], ignore_index=True)
                        
                        # Add email status if available
                        if email_data is not None:
                            email_value = email_data["value"]
                            status_df = pd.concat([status_df, pd.DataFrame([{
                                "id": property_id,
                                "name": property_data["name"],
                                "contact": email_value,
                                "type": "Email",
                                "timestamp": timestamp,
                                "status": "Sent" if success else "Failed",
                                "response": str(response.get("email_status_code", "N/A")) if success else "Error"
                            }])], ignore_index=True)
                    
                    st.session_state.status_df = status_df
                
                # Show success and status
                st.success("Notifications sent successfully!")
                
                # Display detailed status
                st.subheader("Notification Status")
                st.dataframe(status_df, use_container_width=True)
                
                # Option to restart process
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Start New Process"):
                        for key in list(st.session_state.keys()):
                            if key != "step":
                                del st.session_state[key]
                        st.session_state.step = 1
                        st.rerun()
                        
                with col2:
                    if st.button("Download Notification Report"):
                        csv = status_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV Report",
                            data=csv,
                            file_name="notification_report.csv",
                            mime="text/csv",
                        )
    else:
        st.warning("No recipients selected. Please select at least one recipient to send notifications.")
        
        if st.button("⬅️ Back to Contact Selection"):
            st.session_state.step = 4
            st.rerun()