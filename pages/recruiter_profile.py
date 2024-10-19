from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_recruiter_profile,update_recruiter_profile,validate_username,validate_phone,validate_email,get_user_emails,get_user_phones,update_user_profile,get_company_contacts,fetch_user
from time import sleep

make_sidebar()

if "user_id" not in st.session_state and not st.session_state.get("recruiter_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

def save_profile():
    profile_data = {
        "full_name" : full_name,
        "phone": phone,
        "email": email,
        "company_name": company_name,
        'office_location': office_location,
        'company_contact': company_contact,
        'company_email': company_email,
        'company_website': company_website
        
    }
    update_recruiter_profile(st.session_state.user_id, profile_data)
    update_user_profile(st.session_state.user_id, users_data)

    
    st.session_state.username = full_name
    st.success("Profile updated successfully!")
    sleep(0.5)
    st.rerun()

profile = fetch_recruiter_profile(st.session_state.user_id)
user = fetch_user(st.session_state.user_id)

st.markdown("""
    <style>
        .profile-title {
            color: #4CAF50;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
        }
        .profile-subheader {
            color: white;
            font-size: 24px;
            margin-top: 20px;
        }
        .profile-section {
            margin-bottom: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        .profile-section h3 {
            color: #4CAF50;
        }
        .profile-input {
            margin-bottom: 10px;
        }
        .stAlert {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

if profile:
    st.markdown("<h1 class='profile-title'>Profile 📄</h1>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<h2 class='profile-subheader'>Basic Info</h2>", unsafe_allow_html=True)

    full_name = st.text_input("Full Name", profile.get('full_name', ''))
    phone = st.text_input("Phone", profile.get('phone', ''))
    email = st.text_input("Email", profile.get('email', ''))
    password = st.text_input("New Password", type="password")

    st.markdown("</div>", unsafe_allow_html=True)

    users_data = {
        "username": full_name,
        "phone": phone,
        "email": email,
        "password": password
    }
    edit_flag = True

    st.markdown("<h2 class='profile-subheader'>Professional Information</h2>", unsafe_allow_html=True)
    company_name = st.text_input("Company Name", profile.get('company_name', ''))
    office_location = st.text_input("Office Location", profile.get('office_location', ''))
    company_contact = st.text_input("Company Contact Number", profile.get('company_contact', ''))
    company_email = st.text_input("Company Email", profile.get('company_email', ''))
    company_website = st.text_input("Company Website", profile.get('company_website', ''))
    
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Save Information"):
        if full_name != profile.get('full_name'):
            if not validate_username(full_name) or not full_name:
                st.warning('Invalid Name')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["username"] = full_name
        
        if phone != profile.get('phone'):
            if not validate_phone(phone):
                st.warning('Invalid Phone Number')
                sleep(0.5)
                edit_flag = False
            elif phone in get_user_phones():
                st.warning('Phone Number already exists')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["phone"] = phone

        if email != profile.get('email'):
            if not validate_email(email):
                st.warning('Invalid Email Address')
                sleep(0.5)
                edit_flag = False
            elif email in get_user_emails():
                st.warning('Email Address already exists')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["email"] = email

        if company_contact != profile.get('company_contact', ''):
            if not validate_phone(company_contact):
                st.warning('Invalid Company Contact Number')
                sleep(0.5)
                edit_flag = False
            elif company_contact in get_company_contacts():
                st.warning('Company Contact Number already exists')
                sleep(0.5)
                edit_flag = False
        if not password:
            users_data["password"] = user.get('password')

        elif password:
            if len(password) < 6 or not password:
                st.warning("Password is Too Short (Minimum 6 characters)")
                sleep(0.5)
                edit_flag = False
            else:
                users_data["password"] = password

        if edit_flag:
            save_profile()
        else:
            st.rerun()

else:
    st.error("Unable to fetch profile information. Please try again later.")
