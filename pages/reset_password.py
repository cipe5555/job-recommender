import streamlit as st
from navigation import make_sidebar
from dependencies import fetch_user_by_email,update_user_profile, Email
import string
import random

def forgot_password():
    make_sidebar()

    st.subheader("Please enter your email to reset your password:")
    email = st.text_input("Email")

    if st.button("Reset Password", type="primary"):
        try:
            user = fetch_user_by_email(email)
            if user:
                S = 10
                ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))    
                new_password = str(ran)
                user_data = {"password": new_password}
                update_user_profile(user.get("user_id"), user_data)

                # Send the new password via email
                email_sender = Email()
                subject = "Your Password Has Been Reset"
                html_content = f"<p>Your account password for JobRec has been reset. Your new password is: <strong>{new_password}</strong></p>"
                email_sender.send_email(html_content, email, subject)

                st.success("Your password has been reset successfully and sent to your email.")

            else:
                st.error("No user found with this email address.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    if st.button("Back to Landing Page"):
        st.switch_page("landing_page.py")

forgot_password()
