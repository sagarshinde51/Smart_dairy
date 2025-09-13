import streamlit as st
import mysql.connector
import pandas as pd
import re

# ----------------- DATABASE CONFIG -----------------
host = "82.180.143.66"
user = "u263681140_AttendanceInt"
password = "SagarAtten@12345"
database = "u263681140_Attendance"

def get_connection():
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

# Function to fetch data from any table
def fetch_data(table_name):
    try:
        conn = get_connection()
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
        conn = get_connection()
        cursor = conn.cursor()

        sql = """INSERT INTO Farmers_data 
                 (RFID_no, adhar_no, farmer_name, address, mobile_no, email, password, bank, account_no, IFSC_code, cattle_type)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        cursor.execute(sql, data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False


# ----------------- SESSION INIT -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_type" not in st.session_state:
    st.session_state.login_type = None
if "farmer_id" not in st.session_state:
    st.session_state.farmer_id = None


# ----------------- LOGIN PAGE -----------------
if not st.session_state.logged_in:
    st.title("🔐 Login Page")

    login_type = st.radio("Select Login Type", ["Admin", "Farmer"])

    # --------- ADMIN LOGIN ----------
    if login_type == "Admin":
        username = st.text_input("Admin Username")
        password = st.text_input("Admin Password", type="password")

        if st.button("Login as Admin"):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.session_state.login_type = "Admin"
                st.success("✅ Admin Login successful!")
                st.rerun()
            else:
                st.error("Invalid admin username or password")

    # --------- FARMER LOGIN ----------
    elif login_type == "Farmer":
        userid = st.text_input("Enter RFID No or Mobile No")
        password = st.text_input("Password", type="password")

        if st.button("Login as Farmer"):
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM Farmers_data WHERE (RFID_no=%s OR mobile_no=%s) AND password=%s",
                    (userid, userid, password)
                )
                farmer = cursor.fetchone()
                conn.close()

                if farmer:
                    st.session_state.logged_in = True
                    st.session_state.login_type = "Farmer"
                    st.session_state.farmer_id = farmer["RFID_no"]
                    st.success(f"✅ Welcome, {farmer['farmer_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Database Error: {e}")


# ----------------- AFTER LOGIN -----------------
if st.session_state.logged_in:

    # ----------------- ADMIN DASHBOARD -----------------
    if st.session_state.login_type == "Admin":
        tab1, tab2, tab3 = st.tabs(["🥛 Milk Records", "📝 Farmer Registration", "📋 Farmers Data"])

        # TAB 1 - Milk Records
        with tab1:
            st.header("🥛 Milk Records")
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
                df_milk = fetch_data("Milk_Records")
                if not df_milk.empty:
                    st.dataframe(df_milk.sort_values(by="Date", ascending=False))
                else:
                    st.info("No Milk Records found.")

        # TAB 2 - Farmer Registration
        with tab2:
            st.header("📝 Farmer Registration Form")

            with st.form("farmer_form"):
                RFID_no = st.text_input("RFID Number")
                adhar_no = st.text_input("Aadhar No (12 digits)")
                farmer_name = st.text_input("Farmer Name")
                address = st.text_area("Address")
                mobile_no = st.text_input("Mobile No (10 digits)")
                email = st.text_input("Email Address")
                password1 = st.text_input("Password", type="password")
                password2 = st.text_input("Confirm Password", type="password")
                bank = st.selectbox("Select Bank", ["", "SBI", "BOI", "BOM", "Axis", "HDFC", "ICICI", "PNB", "Canara"])
                account_no = st.text_input("Bank Account No")
                IFSC_code = st.text_input("IFSC Code")

                st.markdown("### Select Cattle Type")
                cattle_buffalo = st.checkbox("Buffalo")
                cattle_cow = st.checkbox("Cow")

                submit = st.form_submit_button("Submit")

                if submit:
                    cattle_type = []
                    if cattle_buffalo:
                        cattle_type.append("Buffalo")
                    if cattle_cow:
                        cattle_type.append("Cow")
                    cattle_type = ",".join(cattle_type) if cattle_type else None

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
                        data = (RFID_no, adhar_no, farmer_name, address, mobile_no, email,
                                password1, bank, account_no, IFSC_code, cattle_type)
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


    # ----------------- FARMER DASHBOARD -----------------
    elif st.session_state.login_type == "Farmer":
        tab1, tab2, tab3 = st.tabs(["🥛 My Milk Records", "👤 My Profile", "✏️ Update Info"])

        # TAB 1 - My Milk Records
        with tab1:
            st.header("🥛 My Milk Records")
            if st.session_state.farmer_id:
                df_milk = fetch_data("Milk_Records")
                df_milk = df_milk[df_milk["RFID_no"] == st.session_state.farmer_id]
                if not df_milk.empty:
                    st.dataframe(df_milk.sort_values(by="Date", ascending=False))
                else:
                    st.info("No Milk Records found for your account.")
            else:
                st.error("Farmer ID not found in session.")

        # TAB 2 - My Profile
        with tab2:
            st.header("👤 My Profile")
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Farmers_data WHERE RFID_no=%s", (st.session_state.farmer_id,))
                farmer = cursor.fetchone()
                conn.close()

                if farmer:
                    st.write(f"**Farmer Name:** {farmer['farmer_name']}")
                    st.write(f"**Mobile No:** {farmer['mobile_no']}")
                    st.write(f"**Email:** {farmer['email']}")
                    st.write(f"**Address:** {farmer['address']}")
                    st.write(f"**Bank:** {farmer['bank']} ({farmer['account_no']})")
                    st.write(f"**IFSC Code:** {farmer['IFSC_code']}")
                    st.write(f"**Cattle Type:** {farmer['cattle_type']}")
                else:
                    st.warning("Farmer profile not found.")
            except Exception as e:
                st.error(f"Database Error: {e}")

        # TAB 3 - Update Info (future feature)
        with tab3:
            st.header("✏️ Update Info")
            st.info("This section can be used to update farmer details (not implemented yet).")


    # ----------------- LOGOUT -----------------
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.login_type = None
        st.session_state.farmer_id = None
        st.success("Logged out successfully!")
        st.rerun()
