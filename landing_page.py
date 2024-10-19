import streamlit as st
from navigation import make_sidebar

# Set the page configuration at the very beginning
st.set_page_config(page_title='Job Recommendation System', page_icon='🐍', initial_sidebar_state='collapsed')

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
            padding: 20px;
            border-radius: 10px;
        }
        .title {
            font-size: 3em;
            color: #FFFFFF;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .subheader {
            font-size: 1.5em;
            color: #BFBFBF;
            text-align: center;
            margin-bottom: 20px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            border-radius: 5px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    make_sidebar()
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">🐍Welcome to JobRec System🐍</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Please select your role:</div>', unsafe_allow_html=True)


    if st.button('🧑 Job Seeker'):
        # Set session state for role and redirect
        st.session_state.role = 'job_seeker'
        st.session_state.redirect = True
        st.switch_page("pages/job_seeker_login_page.py")

    if st.button('💼 Recruiter'):
        # Handle recruiter action 
        st.session_state.role = 'recruiter'
        st.session_state.redirect = True
        st.switch_page("pages/recruiter_login_page.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
