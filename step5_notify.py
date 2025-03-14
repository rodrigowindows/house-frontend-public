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
    """Return generic sample scraped data with multiple owners for the same property ID."""
    import pandas as pd
    
    # Create a sample DataFrame with multiple owners for the same property ID
    sample_data = pd.DataFrame({
        "id": ["TEST-PROPERTY-ID"] * 9,  # Same property ID for all contacts
        "address": ["123 Test Street, Test City, FL 12345"] * 9,
        "current_address": ["123 Test Street, Test City, FL 12345"] * 9,
        "name": ["Test Owner 1", "Test Owner 1", "Test Owner 1", 
                "Test Owner 2", "Test Owner 2", "Test Owner 2",
                "Test Owner 3", "Test Owner 3", "Test Owner 3"],
        "type": ["phone_number", "phone_number", "email",
                "phone_number", "phone_number", "email",
                "phone_number", "phone_number", "email"],
        "value": ["(111) 111-1111", "(111) 111-2222", "test1@example.com",
                 "(222) 222-1111", "(222) 222-2222", "test2@example.com",
                 "(333) 333-1111", "(333) 333-2222", "test3@example.com"],
        "selected": [True] * 9
    })
    
    return sample_data

def select_first_contacts():
    """
    Direct implementation to select one phone and one email per unique owner name.
    """
    try:
        st.write("Running direct implementation of select_first_contacts")
        
        # Get current data from session state
        if not hasattr(st.session_state, 'final_data') or st.session_state.final_data is None:
            st.error("No data in session state")
            return None
            
        # Create a copy of the data to work with
        all_contacts_df = st.session_state.final_data.copy()
        st.write(f"Starting with {len(all_contacts_df)} contacts, {len(all_contacts_df['name'].unique())} unique names")
        
        # Convert to records for easier processing
        all_contacts = all_contacts_df.to_dict('records')
        st.write(f"Converted {len(all_contacts)} rows to dictionary records")
        
        # Get unique names
        unique_names = list(set([contact['name'] for contact in all_contacts]))
        st.write(f"Found {len(unique_names)} unique names: {unique_names}")
        
        # Store selected contacts
        selected_contacts = []
        
        # Process each unique name
        for name in unique_names:
            st.write(f"Processing {name}")
            
            # Get all contacts for this name
            name_contacts = [c for c in all_contacts if c['name'] == name]
            
            # Find first phone number
            phone_contacts = [c for c in name_contacts if c['type'] == 'phone_number']
            if phone_contacts:
                selected_contacts.append(phone_contacts[0])
                st.write(f"Added phone for {name}: {phone_contacts[0]['value']}")
            
            # Find first email
            email_contacts = [c for c in name_contacts if c['type'] == 'email']
            if email_contacts:
                selected_contacts.append(email_contacts[0])
                st.write(f"Added email for {name}: {email_contacts[0]['value']}")
        
        # Convert back to DataFrame
        if selected_contacts:
            result_df = pd.DataFrame(selected_contacts)
            
            # Add send_to column
            result_df['send_to'] = True
            
            # Save to session state
            st.session_state.final_data = result_df
            
            # Show success
            st.write(f"Successfully selected {len(result_df)} contacts from {len(result_df['name'].unique())} unique owners")
            return result_df
        else:
            st.error("No contacts were selected")
            return None
            
    except Exception as e:
        import traceback
        st.error(f"Error in select_first_contacts: {str(e)}")
        st.error(traceback.format_exc())
        return None

def send_marketing_notification(contact_dict):
    """Send notification via the marketing API."""
    try:
        # API endpoint
        API_ENDPOINT = "http://llmmsi.a.pinggy.link/marketing/start"
        
        # Extract contact information
        name = contact_dict["name"]
        address = contact_dict["address"]
        
        # Create payload - always include all fields with empty strings instead of None
        payload = {
            "name": name,
            "address": address,
            "phone_number": "",  # Default to empty string instead of None
            "email": ""          # Default to empty string instead of None
        }
        
        # Update with actual values if available
        if contact_dict["type"] == "phone_number":
            payload["phone_number"] = contact_dict["value"]
        elif contact_dict["type"] == "email":
            payload["email"] = contact_dict["value"]
        
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
            st.experimental_rerun()
    
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
                st.experimental_rerun()
    
    # Test your contacts button
    if st.button("🔍 Analyze Current Contacts"):
        if hasattr(st.session_state, 'final_data') and st.session_state.final_data is not None:
            data = st.session_state.final_data
            st.write(f"Current data shape: {data.shape}")
            st.write(f"Unique names: {sorted(data['name'].unique())}")
            st.write(f"Contacts per name:")
            for name in sorted(data['name'].unique()):
                name_data = data[data['name'] == name]
                st.write(f"  - {name}: {len(name_data)} contacts")
                for type_val in name_data['type'].unique():
                    type_count = len(name_data[name_data['type'] == type_val])
                    st.write(f"    - {type_val}: {type_count}")
    
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
            unique_editor_key = f"editor_{owner_id}_{widget_counter}_{owner_name}"
            
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
            owners_data[f"{owner_id}_{owner_name}"] = edited_contacts
    
    # Combine all the edited data
    updated_contacts = pd.DataFrame()
    for key, edited_data in owners_data.items():
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
                st.experimental_rerun()
                
        with col2:
            send_button = st.button("Send Notifications", type="primary")
            
            if send_button and not selected_contacts.empty:
                # Call API to send notifications
                with st.spinner("Sending notifications..."):
                    # Prepare for status tracking
                    status_df = pd.DataFrame(columns=[
                        "id", "name", "contact", "type", "timestamp", "status", "response"
                    ])
                    
                    # Process each contact one by one (each row is a separate API call)
                    for idx, contact in selected_contacts.iterrows():
                        # Create the contact dictionary directly from the row
                        contact_dict = contact.to_dict()
                        
                        # Send notification (one API call per contact)
                        response, success = send_marketing_notification(contact_dict)
                        
                        # Record status
                        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Add status entry
                        status_df = pd.concat([status_df, pd.DataFrame([{
                            "id": contact["id"],
                            "name": contact["name"],
                            "contact": contact["value"],
                            "type": "Call/SMS" if contact["type"] == "phone_number" else "Email",
                            "timestamp": timestamp,
                            "status": "Sent" if success else "Failed",
                            "response": str(response) if success else "Error"
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
                        st.experimental_rerun()
                        
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
            st.experimental_rerun()
