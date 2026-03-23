import streamlit as st
from auth.auth_utils import auth

def signup_ui():
    st.subheader("📝 Create Account")

    # Input fields
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    # Signup button
    if st.button("Signup"):
        try:
            # Create user in Firebase
            auth.create_user_with_email_and_password(email, password)

            st.success("Account created successfully ✅")

        except Exception as e:
            st.error("Signup failed ❌")