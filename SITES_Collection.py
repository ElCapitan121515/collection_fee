import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 🔘 Logout button
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("You have been logged out. Please return to the home page.")
    st.stop()

# ✅ Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# ✅ Streamlit UI
st.title("📋 Student Collection Form")

# Section selection
sheet_name = st.selectbox("Select Section (sheet_name)", ["- SELECT -", 
    "BSCpE1A", "BSCpE1B", "BSCpE1C", "BSCpE1D", "BSCpE2A", "BSCpE2B", "BSCpE2C", "BSCpE2D",
    "BSCpE3A", "BSCpE3B", "BSCpE4A", "BSEE 1A-1", "BSEE 1A-2", "BSEE 1B-1", "BSEE 1B-2",
    "BSEE 1C-1", "BSEE 1C-2", "BSEE 2A-1", "BSEE 2A-2", "BSEE 2B-1", "BSEE 2B-2", 
    "BSEE 2C-1", "BSEE 2C-2", "BSEE 3A-1", "BSEE 3A-2", "BSEE 3B-1", "BSEE 4A-1", "BSEE 4A-2",
    "BSINFOTECH 1A-1", "BSINFOTECH 1A-2", "BSINFOTECH 1B-1", "BSINFOTECH 1B-2", 
    "BSINFOTECH 1C-1", "BSINFOTECH 1C-2", "BSINFOTECH 2A-1", "BSINFOTECH 2A-2", 
    "BSINFOTECH 2B-1", "BSINFOTECH 2B-2", "BSINFOTECH 2C-1", "BSINFOTECH 2C-2", 
    "BSINFOTECH 3A-1", "BSINFOTECH 3A-2", "BSINFOTECH 3B-1", "BSINFOTECH 3B-2", 
    "BSINFOTECH 3C-1", "BSINFOTECH 3C-2", "BSINFOTECH 4A", "EET 3A-1", "EET 3A-2"])
if sheet_name == "- SELECT -":
    st.stop()

# Open the selected worksheet
worksheet = client.open("SITES_Collection").worksheet(sheet_name)

# Input field for ID Number
id_number = st.text_input("Enter ID Number")

# Initialize default values
username = ""
first_collection = 0
second_collection = 0
receipt_number = ""
status = ""
receipt_enabled = True
first_enabled = False
second_enabled = False
row_index = None

# 🔍 Lookup student record
if id_number:
    try:
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        match = df[df.iloc[:, 2] == id_number]

        if not match.empty:
            row_index = match.index[0] + 2  # Offset: header + 1-based index
            username = match.iloc[0, 3]
            first_collection = match.iloc[0, 4]
            second_collection = match.iloc[0, 5]
            receipt_number = match.iloc[0, 6]
            status = match.iloc[0, 7]
            st.success(f"✅ Data found for ID Number: {id_number}")

            # ✅ Enable/disable logic based on values
            if first_collection == 100 and second_collection == 100:
                first_enabled = False
                second_enabled = False
                receipt_enabled = False
            elif first_collection == 0:
                first_enabled = True
                second_enabled = False
                receipt_enabled = True
            elif first_collection == 100:
                first_enabled = False
                second_enabled = True # if second_collection == 0 else False
                receipt_enabled = True
            else:
                first_enabled = True
                second_enabled = False
                receipt_enabled = True
        else:
            st.warning("⚠️ ID Number not found in the sheet.")
    except Exception as e:
        st.error(f"❌ Error during lookup: {e}")

# 📝 Collection Update Form
with st.form("collection_form"):
    st.text_input("Username", value=username, disabled=True)

    # First Collection
    if first_enabled:
        updated_first = st.selectbox("First Collection", [0, 100],
                                     index=0 if first_collection == 0 else 1)
    else:
        updated_first = first_collection
        st.selectbox("First Collection", [first_collection], index=0, disabled=True)

    # Second Collection
    if second_enabled:
        updated_second = st.selectbox("Second Collection", [0, 100],
                                      index=0 if second_collection == 0 else 1)
    else:
        updated_second = second_collection
        st.selectbox("Second Collection", [second_collection], index=0, disabled=True)

    # Receipt Number
    if receipt_enabled:
        updated_receipt = st.text_input("Receipt Number", value=receipt_number)
    else:
        updated_receipt = receipt_number
        st.text_input("Receipt Number", value=receipt_number, disabled=True)

    st.text_input("Status", value=status, disabled=True)

    submit_button = st.form_submit_button("Submit")

# 🔔 Popup confirmation dialog (Streamlit 1.41+)
@st.dialog("⚠️ Confirm Submission")
def confirm_submission():
    st.write("Are you sure you want to submit this update?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Submit"):
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                worksheet.update_cell(row_index, 1, timestamp)       # Column A
                worksheet.update_cell(row_index, 4, username)        # Column D

                if first_enabled:  # ✅ update only if enabled
                    worksheet.update_cell(row_index, 5, updated_first)   # Column E

                if second_enabled:  # ✅ update only if enabled
                    worksheet.update_cell(row_index, 6, updated_second)  # Column F

                if receipt_enabled:  # ✅ update only if enabled
                    worksheet.update_cell(row_index, 7, updated_receipt) # Column G

                st.success("✅ Data successfully updated in Google Sheet!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error updating data: {e}")
    with col2:
        if st.button("❌ Cancel"):
            st.info("Submission cancelled.")

# ✅ Handle submission
if submit_button and row_index:
    confirm_submission()
elif submit_button and not row_index:
    st.error("⚠️ Cannot submit: ID Number not found.")

# 📄 Optional: Show all data in table
if st.button("📄 Display Spreadsheet Data"):
    try:
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")
