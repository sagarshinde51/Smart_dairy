import streamlit as st
import mysql.connector
import re

# Database connection details
host = "82.180.143.66"
user = "u263681140_AttendanceInt"
password = "SagarAtten@12345"
database = "u263681140_Attendance"

# Function to insert farmer data
def insert_farmer(data):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
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


# Streamlit UI
st.title("🐄 Farmer Registration Form")

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
        # Collect cattle type
        cattle_type = []
        if cattle_buffalo:
            cattle_type.append("Buffalo")
        if cattle_cow:
            cattle_type.append("Cow")
        cattle_type = ",".join(cattle_type)

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
        else:
            data = (adhar_no, farmer_name, address, mobile_no, email, password1, bank, account_no, IFSC_code, cattle_type)
            if insert_farmer(data):
                st.success("✅ Farmer record inserted successfully!")
