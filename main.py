import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials



# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Spreadsheet and Sheet
spreadsheet = client.open("LSG_Collection")
worksheet = spreadsheet.worksheet("User_Account")

# Get all user data from the sheet
user_data = worksheet.get_all_records()

# Login UI
st.title("🔐 Student Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        user_found = False
        for user in user_data:
            if user["username"] == username and str(user["password"]) == str(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                user_found = True
                #st.success("✅ Login successful!")
                
               # st.experimental_rerun()
                break

        if not user_found:
            st.error("❌ Invalid username or password")
else:
    st.success(f"✅ Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
       # st.experimental_rerun()
