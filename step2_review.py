import streamlit as st
import pandas as pd
from utils import navigation_buttons

def show():
    """Display the review and edit data step."""
    st.header("Step 2: Review and Edit Property Data")
    
    # If no data exists, show option to create some manually
    if st.session_state.data is None:
        st.warning("No data available from previous step.")
        
        with st.form("create_data_form"):
            st.write("Add property data manually to continue:")
            
            # Property form
            cols1 = st.columns(2)
            with cols1[0]:
                acct_num = st.text_input("Account Number")
                owner_name = st.text_input("Owner Name")
            with cols1[1]:
                status = st.selectbox("Account Status", ["Unpaid", "Paid", "Pending"])
                property_address = st.text_input("Property Address")
                
            balance = st.number_input("Balance Amount", min_value=0.0, step=100.0)
            
            submitted = st.form_submit_button("Add Property Data")
            
            if submitted:
                st.session_state.data = pd.DataFrame({
                    "Account Number": [acct_num if acct_num else "00-00-00-0000-00000"],
                    "Account Status": [status],
                    "Owner Name": [owner_name if owner_name else "New Owner"],
                    "Property Address": [property_address if property_address else "Unknown Address"],
                    "Balance Amount": [balance],
                    "Assessed Value": [350000],
                    "Tax Yr": [2023],
                    "Roll Yr": [2023]
                })
                st.success("Property data added successfully!")
                st.experimental_rerun()
    else:
        # Create an editable dataframe
        st.markdown("### Property Tax Certificate Data")
        st.write("You can add, edit, or delete rows as needed.")
        
        # Get the column names from the dataframe
        columns = st.session_state.data.columns.tolist()
        
        # Create column config based on data columns
        column_config = {}
        
        # Configure specific columns that we know about
        if "Account Number" in columns:
            column_config["Account Number"] = st.column_config.TextColumn("Account Number", help="Property account number")
        
        if "Account Status" in columns:
            column_config["Account Status"] = st.column_config.SelectboxColumn(
                "Account Status", 
                help="Current status of the account", 
                options=["Unpaid", "Paid", "Pending"]
            )
            
        if "Owner Name" in columns:
            column_config["Owner Name"] = st.column_config.TextColumn("Owner Name", help="Property owner's name")
            
        if "Balance Amount" in columns:
            column_config["Balance Amount"] = st.column_config.NumberColumn(
                "Balance Amount", 
                help="Amount due on certificate",
                format="$%.2f"
            )
            
        if "Assessed Value" in columns:
            column_config["Assessed Value"] = st.column_config.NumberColumn(
                "Assessed Value", 
                help="Assessed property value",
                format="$%.2f"
            )
        
        # Create the data editor with the configured columns
        edited_data = st.data_editor(
            st.session_state.data, 
            num_rows="dynamic",
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )
        
        # Save the edited data
        st.session_state.selected_data = edited_data
        
        # Add property data manually option
        with st.expander("Add Property Data Manually"):
            with st.form("add_manual_property_data"):
                st.write("Add a new property record:")
                
                cols = st.columns(3)
                with cols[0]:
                    new_acct_num = st.text_input("Account Number")
                with cols[1]:
                    new_owner = st.text_input("Owner Name")
                with cols[2]:
                    new_status = st.selectbox("Account Status", ["Unpaid", "Paid", "Pending"])
                
                cols2 = st.columns(2)
                with cols2[0]:
                    new_address = st.text_input("Property Address")
                with cols2[1]:
                    new_balance = st.number_input("Balance Amount", min_value=0.0, step=100.0)
                
                submitted = st.form_submit_button("Add Property")
                
                if submitted:
                    # Create new record with fields matching our data structure
                    new_record = pd.DataFrame({
                        "Account Number": [new_acct_num if new_acct_num else "00-00-00-0000-00000"],
                        "Account Status": [new_status],
                        "Owner Name": [new_owner if new_owner else "New Owner"],
                        "Property Address": [new_address if new_address else "Unknown Address"],
                        "Balance Amount": [new_balance],
                        "Assessed Value": [350000],  # Default value
                        "Tax Yr": [2023],
                        "Roll Yr": [2023],
                        "Cert Status": ["Pending"],
                        "Deed Status": ["-- None --"]
                    })
                    
                    # Add any missing columns from the original data
                    for col in edited_data.columns:
                        if col not in new_record.columns:
                            new_record[col] = None
                    
                    # Append to existing data
                    updated_data = pd.concat([edited_data, new_record], ignore_index=True)
                    st.session_state.data = updated_data
                    st.session_state.selected_data = updated_data
                    st.success("Property record added successfully!")
                    st.experimental_rerun()
    
    # Options to export data
    if st.session_state.data is not None and not st.session_state.data.empty:
        with st.expander("Export Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export as CSV"):
                    csv = st.session_state.data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="processed_data.csv",
                        mime="text/csv",
                    )
            
            with col2:
                if st.button("Export as JSON"):
                    json_str = st.session_state.data.to_json(orient="records")
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name="processed_data.json",
                        mime="application/json",
                    )
    
    # Navigation buttons
    st.markdown("---")
    navigation_buttons(back_label="⬅️ Back to Upload", next_label="Proceed to Data Scraping ➡️")