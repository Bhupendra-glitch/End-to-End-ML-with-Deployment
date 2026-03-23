# Show logged-in user
st.sidebar.success(f"👤 {st.session_state['user']}")

# Logout button
if st.sidebar.button("Logout"):
    del st.session_state["user"]
    st.rerun()