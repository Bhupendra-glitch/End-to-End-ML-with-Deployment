import streamlit as st
from auth.auth_utils import auth

def login_ui():
    st.subheader("🔐 Login")

    # Input fields
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        try:
            # Authenticate user
            user = auth.sign_in_with_email_and_password(email, password)

            # Store user session
            st.session_state["user"] = email

            st.success("Login successful ✅")

        except:
            st.error("Invalid credentials ❌")