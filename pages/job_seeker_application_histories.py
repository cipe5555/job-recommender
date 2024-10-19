from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_job_seeker_profile, fetch_application_by_job_seeker, fetch_job_by_id, convert_to_malaysia_time

make_sidebar()

if "user_id" not in st.session_state or not st.session_state.get("job_seeker_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

job_seeker_profile = fetch_job_seeker_profile(st.session_state.user_id)
job_seeker_id = job_seeker_profile.get('user_id')

st.header("Application Histories")

def display_histories(job_seeker_id, page=1, per_page=10):
    applications = fetch_application_by_job_seeker(job_seeker_id)
    
    # Sort applications by date in descending order (latest first)
    applications = sorted(applications, key=lambda app: app.get('created_at', ''), reverse=True)
    
    total_apps = len(applications)
    total_pages = (total_apps + per_page - 1) // per_page

    if total_apps == 0:
        st.write("No applications found.")
        total_pages += 1

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_apps = applications[start_idx:end_idx]

    for idx, app in enumerate(current_page_apps, start=start_idx + 1):
        job_info = fetch_job_by_id(app['job_id'])
        with st.expander(f"Application {idx}: {job_info.get('title', 'N/A').title()} at {job_info.get('company', 'N/A')}"):
            st.write(f"**Job Title:** {job_info.get('title', 'N/A').title()}")
            st.write(f"**Company:** {job_info.get('company', 'N/A')}")
            st.write(f"**Location:** {job_info.get('location', 'N/A')}")
            st.write(f"**Applied On:** {convert_to_malaysia_time(app.get('created_at', 'N/A'))}")
            st.write(f"**Application Status:** {app.get('status', 'N/A')}")
            # st.markdown("---") 

    # Pagination controls
    st.write(f"Page {page} of {total_pages}")
    col1, col2, col3 = st.columns(3)
    if page > 1:
        if col1.button("Previous"):
            display_histories(job_seeker_id, page - 1, per_page)
    if page < total_pages:
        if col3.button("Next"):
            display_histories(job_seeker_id, page + 1, per_page)
    
    if st.button("Back to Home"):
        st.switch_page("pages/job_seeker_home.py")

if __name__ == "__main__":
    if job_seeker_id:
        display_histories(job_seeker_id)
