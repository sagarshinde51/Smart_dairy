import streamlit as st
import mysql.connector
import pandas as pd
import re

# Database connection details
host = "82.180.143.66"
user = "u263681140_AttendanceInt"
password = "SagarAtten@12345"
database = "u263681140_Attendance"


# Function to fetch data from any table
def fetch_data(table_name):
    try:
        conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()


# Function to insert farmer data
def insert_farmer(data):
    try:
        conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        cursor = conn.cursor()

        sql = """INSERT INTO Farmers_data 
                 (adhar_no, farmer_name, address, mobile_no, email, password, bank, account_no, IFSC_code, cattle_type)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        cursor.execute(sql, data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False


# ----------------- LOGIN PAGE -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# ----------------- AFTER LOGIN -----------------
if st.session_state.logged_in:
    tab1, tab2, tab3 = st.tabs(["🥛 Milk Records", "📝 Farmer Registration", "📋 Farmers Data"])

    # TAB 1 - Milk Records
    with tab1:
        st.header("🥛 Milk Records")

        # RFID Search
        search_rfid = st.text_input("🔍 Enter RFID Number to Search")
        if st.button("Search by RFID"):
            if search_rfid.strip():
                df_milk = fetch_data("Milk_Records")
                df_milk = df_milk[df_milk["RFID_no"] == search_rfid.strip()]
                if not df_milk.empty:
                    st.dataframe(df_milk.sort_values(by="Date", ascending=False))
                else:
                    st.warning(f"No records found for RFID: {search_rfid}")
            else:
                st.error("Please enter RFID number before searching.")
        else:
            # Default view - show all records
            df_milk = fetch_data("Milk_Records")
            if not df_milk.empty:
                st.dataframe(df_milk.sort_values(by="Date", ascending=False))
            else:
                st.info("No Milk Records found.")    # TAB 2 - Farmer Registration
    with tab2:
        st.header("📝 Farmer Registration Form")

        with st.form("farmer_form"):
            adhar_no = st.text_input("Aadhar No (12 digits)")
            farmer_name = st.text_input("Farmer Name")
            address = st.text_area("Address")
            mobile_no = st.text_input("Mobile No (10 digits)")
            email = st.text_input("Email Address")
            password1 = st.text_input("Password", type="password")
            password2 = st.text_input("Confirm Password", type="password")

            # Dropdown for bank
            bank = st.selectbox("Select Bank", 
                                ["", "SBI", "BOI", "BOM", "Axis", "HDFC", "ICICI", "PNB", "Canara"])

            account_no = st.text_input("Bank Account No")
            IFSC_code = st.text_input("IFSC Code")

            # Cattle type checkboxes
            st.markdown("### Select Cattle Type")
            cattle_buffalo = st.checkbox("Buffalo")
            cattle_cow = st.checkbox("Cow")

            submit = st.form_submit_button("Submit")

            if submit:
                # Collect cattle type values
                cattle_type = []
                if cattle_buffalo:
                    cattle_type.append("Buffalo")
                if cattle_cow:
                    cattle_type.append("Cow")
                cattle_type = ",".join(cattle_type) if cattle_type else None

                # Validations
                if not re.match(r"^[0-9]{12}$", adhar_no):
                    st.error("Aadhar must be 12 digits")
                elif not re.match(r"^[0-9]{10}$", mobile_no):
                    st.error("Mobile number must be 10 digits")
                elif "@" not in email:
                    st.error("Invalid email address")
                elif password1 != password2:
                    st.error("Passwords do not match")
                elif bank == "":
                    st.error("Please select a bank")
                elif not cattle_type:
                    st.error("Please select at least one cattle type")
                else:
                    data = (adhar_no, farmer_name, address, mobile_no, email, password1, bank, account_no, IFSC_code, cattle_type)
                    if insert_farmer(data):
                        st.success("✅ Farmer record inserted successfully!")

    # TAB 3 - Farmers Data
    with tab3:
        st.header("📋 Farmers Data")
        df_farmers = fetch_data("Farmers_data")
        if not df_farmers.empty:
            st.dataframe(df_farmers)
        else:
            st.info("No Farmers found.")

    # 🚪 Logout button at bottom (common for all tabs)
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.rerun()
