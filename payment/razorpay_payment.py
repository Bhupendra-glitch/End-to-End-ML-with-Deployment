import streamlit as st
from config.razorpay_config import client
from payment.plans import plans

def payment_ui():
    st.title("💳 Upgrade to Premium")

    # Select plan
    plan = st.selectbox("Choose Plan", list(plans.keys()))

    # Show price
    amount = plans[plan]
    st.write(f"Price: ₹{amount}")

    # Payment button
    if st.button("Proceed to Pay"):

        # Create order in Razorpay
        order = client.order.create({
            "amount": amount * 100,  # convert to paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Store order id
        st.session_state["order_id"] = order["id"]

        st.success("Order created successfully ✅")

        # Show order details
        st.write(f"Order ID: {order['id']}")
        st.write("⚠️ Complete payment using Razorpay Checkout (frontend needed)")