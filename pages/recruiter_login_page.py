import streamlit as st
from dependencies import recruiter_sign_up, fetch_users
from navigation import make_sidebar
from time import sleep

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
            padding: 20px;
            border-radius: 10px;
        }
        .subheader {
            font-size: 2em;
            color: #FFFFFF;
            text-align: center;
            margin-bottom: 20px;
        }
        .stTextInput, .stPasswordInput {
            width: 100%;
            margin-bottom: 20px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            border-radius: 5px;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .stButtonContainer {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .success-message {
            color: #28a745;
            text-align: center;
            margin-top: 20px;
        }
        .error-message {
            color: #dc3545;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

def recruiter_login():
    make_sidebar()
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="subheader">🏢 Login As Recruiter</div>', unsafe_allow_html=True)
    
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Log in", type="primary"):
            try:
                users = fetch_users()
                emails = []
                user_id = []
                usernames = []
                passwords = []
                roles = []

                for user in users:
                    emails.append(user['email'])
                    user_id.append(user['user_id'])
                    usernames.append(user['username'])
                    passwords.append(user['password'])
                    roles.append(user['role'])

                credentials = {emails[index]: {'username': usernames[index], 'user_id': user_id[index], 'password': passwords[index], 'role': roles[index]} for index in range(len(emails))}
                if email in credentials and credentials[email]['password'] == password and credentials[email]['role'] == 2:
                    st.session_state.recruiter_logged_in = True
                    st.session_state.user_id = credentials[email]['user_id']
                    st.session_state.username = credentials[email]['username']
                    st.markdown('<div class="success-message">✅ Logged in successfully!</div>', unsafe_allow_html=True)
                    sleep(0.5)
                else:
                    st.markdown('<div class="error-message">❌ Incorrect Password or Email</div>', unsafe_allow_html=True)
                    sleep(0.5)
                    st.rerun()
            except Exception as e:
                st.markdown(f'<div class="error-message">❌ An error occurred: {str(e)}</div>', unsafe_allow_html=True)

    with col2:
        if st.button("Forgot Password?"):
            st.session_state.forgot_password = True
            st.switch_page("pages/reset_password.py")

    recruiter_sign_up()
    
    if st.session_state.get('recruiter_logged_in', False):
        st.switch_page("pages/recruiter_home.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

recruiter_login()
