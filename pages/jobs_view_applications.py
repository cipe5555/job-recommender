from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_application, fetch_job_seeker_profile_by_id, fetch_recruiter_profile, fetch_job_by_id, update_application_status, convert_to_malaysia_time
from time import sleep

make_sidebar()

if "user_id" not in st.session_state or not st.session_state.get("recruiter_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

if "review_apply_message" not in st.session_state:
    st.session_state.review_apply_message = None

if "last_reviewed_job" not in st.session_state:
    st.session_state.last_reviewed_job = ""

recruiter_profile = fetch_recruiter_profile(st.session_state.user_id)
recruiter_id = recruiter_profile.get('user_id')
job_id = st.session_state.get('selected_job_id')
job_info = fetch_job_by_id(job_id)

if not job_id:
    st.error("No job selected.")
    st.stop()

st.header(f"Applicants for {job_info.get('title').title()}")

def reviewed_apply(application_id, job_seeker_name, job_title):
    update_application_status(application_id)
    st.session_state.reviewed_message = f"Status for applicant: {job_seeker_name} has been changed to: Reviewed."
    st.session_state.last_reviewed_job = job_title

def display_applicants(job_id, recruiter_id, page=1, per_page=10):
    applications = fetch_application(job_id, recruiter_id)
    
    # Sort applications by date in descending order (latest first)
    applications = sorted(applications, key=lambda app: app.get('created_at', ''), reverse=True)
    
    total_apps = len(applications)
    total_pages = (total_apps + per_page - 1) // per_page  # Calculate total pages

    if total_apps == 0:
        st.write("No applications found for this job.")
        total_pages += 1

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_apps = applications[start_idx:end_idx]

    for idx, app in enumerate(current_page_apps, start=start_idx + 1):
        job_seeker_profile = fetch_job_seeker_profile_by_id(app.get('job_seeker_id'))
        application_date = convert_to_malaysia_time(app.get('created_at', 'N/A'))
        job = fetch_job_by_id(app.get('job_id'))

        with st.expander(f"Applicant {idx}: {job_seeker_profile.get('full_name', 'Unknown')}"):
            st.markdown(f"""
                **Applicant Name:** {job_seeker_profile.get('full_name', 'N/A')}\n
                **Email:** {job_seeker_profile.get('email', 'N/A')}\n
                **Phone Number:** {job_seeker_profile.get('phone', 'N/A')}\n
                **Application Date:** {application_date}\n
                **Skills:** {', '.join(job_seeker_profile.get('skills', []))}\n
                **Experience:** {job_seeker_profile.get('years_of_experience', 'N/A')}
            """)
            st.markdown("**Education:**")
            education = job_seeker_profile.get('education', [])
            if education:
                for edu in education:
                    st.markdown(f"""
                        - **Institution:** {edu.get('institution', 'N/A')}
                        - **Major:** {edu.get('major', 'N/A')}
                        - **Graduation Year:** {edu.get('graduation_year', 'N/A')}
                        - **Education Level:** {edu.get('education_level', 'N/A')}
                    """)
            else:
                st.markdown("N/A")
            st.markdown(f"**Status:** {app.get('status', 'N/A')}\n")
            if st.session_state.review_apply_message and st.session_state.last_review_job == app['title']:
                if st.session_state.review_apply_message == f"Status for applicant: {job_seeker_profile.get('full_name', 'N/A')} has been reviewed already.":
                    st.error(st.session_state.review_apply_message)
                else:
                    st.success(st.session_state.review_apply_message)

            if app.get('status') != "Reviewed":
                if st.button(f"Reviewed", key=f"reviewed_{idx}", on_click=reviewed_apply, args=(app.get('application_id'), job_seeker_profile.get('full_name', 'N/A'), job['title'])):
                    st.session_state.last_reviewed_job = job['title'].title()
                    sleep(1.5)
                    st.experimental_rerun()

    # Pagination Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if page > 1:
            st.button("Previous", on_click=display_applicants, args=(job_id, recruiter_id, page - 1))
    with col2:
        st.write(f"Page {page} of {total_pages}")
    with col3:
        if page < total_pages:
            st.button("Next", on_click=display_applicants, args=(job_id, recruiter_id, page + 1))

    if st.button("Back to Home"):
        st.session_state.selected_job_id = None  # Clear the selected job ID before switching pages
        st.session_state.recruiter_home_page = "View Jobs"
        if "reviewed_message" in st.session_state:
            del st.session_state.reviewed_message
        st.switch_page("pages/recruiter_home.py")

if __name__ == '__main__':
    if job_id and recruiter_id:
        display_applicants(job_id, recruiter_id)
