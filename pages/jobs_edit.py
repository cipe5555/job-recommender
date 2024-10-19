from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_recruiter_profile, update_job, fetch_job_by_id, validate_phone, get_company_contacts
from time import sleep

make_sidebar()

if "user_id" not in st.session_state or not st.session_state.get("recruiter_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

profile = fetch_recruiter_profile(st.session_state.user_id)
job_id = st.session_state.get('selected_job_id')

if not job_id:
    st.error("No job selected for editing.")
    st.stop()

st.header("Edit Job")

# Fetch the job details to pre-fill the form
job = fetch_job_by_id(job_id)

if not job:
    st.error("Job not found.")
    st.stop()

job_category_options = [
    "Advertising & Marketing", "Aerospace", "Agriculture", "Computer & Technology",
    "Construction", "Education", "Energy", "Entertainment", "Fashion", "Finance & Economic",
    "Food & Beverage", "Healthcare", "Hospitality", "Manufacturing", "Media & News",
    "Mining", "Pharmaceutical", "Telecommunication", "Transportation"
]

with st.form(key='edit_job_form', clear_on_submit=False):
    title = st.text_input("Job Title", job['title'].title())
    company = st.text_input("Company Name", job['company'])
    location = st.text_input("Location", job['location'])
    salary = st.slider("Salary (RM)", 0, 20000, step=100, value=job['salary'])
    job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Remote"], index=["Full-time", "Part-time", "Contract", "Remote"].index(job['job_type']))
    description = st.text_area("Job Description", job['description'])
    requirements = st.text_area("Job Requirements", job['requirements'])
    company_website = st.text_input("Company Website", job['company_website'])
    company_contact = st.text_input("Company Contact Number", job['company_contact'])
    benefits = st.text_area("Benefits (comma-separated)", ', '.join(job['benefits']))
    job_category = st.selectbox("Job Category", job_category_options, index=job_category_options.index(job['job_category']))
    visibility = st.checkbox("Make Job Visible", value=job['visibility'])

    submit_button = st.form_submit_button(label='Update Job')
    edit_flag = True
    
    if submit_button:
        benefits_list = benefits.split(",") if benefits else []
        if not title:
            st.warning("Job Title Cannot Be Empty")
        elif not company:
            st.warning("Company Name Cannot Be Empty")
        elif not location:
            st.warning("Location Cannot Be Empty")
        elif not description:
            st.warning("Job Description Cannot Be Empty")
        elif not requirements:
            st.warning("Job Requirements Cannot Be Empty")
        elif not company_contact:
            st.warning("Company Contact Cannot Be Empty")
        
        else:
            if company_contact != profile.get('company_contact', ''):
                if not validate_phone(company_contact):
                    st.warning('Invalid Company Contact Number')
                    sleep(0.5)
                    edit_flag = False
                elif company_contact in get_company_contacts():
                    st.warning('Company Contact Number already exists')
                    sleep(0.5)
                    edit_flag = False
            if edit_flag:
                try:
                    update_job(
                        job_id=job_id,
                        title=title,
                        company=company,
                        location=location,
                        salary=salary,
                        job_type=job_type,
                        description=description,
                        requirements=requirements,
                        company_website=company_website,
                        company_contact=company_contact,
                        benefits=benefits_list,
                        job_category=job_category,
                        visibility=visibility
                    )
                    st.success(f"Job: '{title}' updated successfully!")
                    sleep(0.5)
                    st.session_state.selected_job_id = None  # Clear the selected job ID
                    st.session_state.recruiter_home_page = "View Jobs"
                    # st.experimental_rerun()  # Refresh the page
                    st.switch_page("pages/recruiter_home.py")
                except Exception as e:
                    st.error(f"Error updating job: {e}")

if st.button("Back to Home"):
    st.session_state.selected_job_id = None  # Clear the selected job ID before switching pages
    st.session_state.recruiter_home_page = "View Jobs"
    st.switch_page("pages/recruiter_home.py")
    # st.experimental_rerun()  # Optional: Trigger a rerun to refresh and navigate to home
