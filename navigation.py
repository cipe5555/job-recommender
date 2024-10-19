import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    if "user_id" not in st.session_state:
        st.session_state.user_id = ""
    with st.sidebar:
        st.title("JobRec System")

        if st.session_state.get("job_seeker_logged_in", False):
            st.subheader(f'Welcome, {st.session_state["username"]}!')
            st.write("")
            st.write("")
            st.page_link("pages/job_seeker_home.py", label="Home")
            st.page_link("pages/job_seeker_profile.py", label="Profile")
            st.page_link("pages/job_seeker_search_jobs.py", label="Search Jobs")
            st.page_link('pages/user_based.py', label="Job Recommendation (User-Based)")
            st.page_link('pages/profile_based.py', label="Job Recommendation (Profile-Based)")
            st.page_link("pages/job_seeker_application_histories.py", label="Application Histories")


            st.write("")
            st.write("")

            if st.button("Log out"):
                logout(1)

        elif st.session_state.get("recruiter_logged_in", False):
            st.subheader(f'Welcome, {st.session_state["username"]}!')
            st.write("")
            st.write("")
            st.page_link("pages/recruiter_home.py", label="Home")
            st.page_link("pages/recruiter_profile.py", label="Profile")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout(2)
        
        elif not (st.session_state.get("recruiter_logged_in", False) and st.session_state.get("job_seeker_logged_in", False)):
            st.write("")
            st.page_link("landing_page.py", label="Landing Page")



def logout(role):
    if role == 1:
        st.session_state.job_seeker_logged_in = False
    elif role == 2:
        st.session_state.recruiter_logged_in = False
    st.session_state.clear()
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("landing_page.py")