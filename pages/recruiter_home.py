from navigation import make_sidebar
import streamlit as st
import pandas as pd
import datetime
from time import sleep
from dependencies import (
    insert_job,
    fetch_recruiter_profile,
    fetch_specific_jobs,
    delete_job,
    convert_to_malaysia_time,
    fetch_job_application_counts,
    validate_phone,
    get_company_contacts
)

make_sidebar()

if "user_id" not in st.session_state and not st.session_state.get("recruiter_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

profile = fetch_recruiter_profile(st.session_state.user_id)

# Custom CSS for fade-in effect
st.markdown("""
    <style>
        .fade-in {
            animation: fadeIn 3s ease-in-out;
        }

        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        .apply-btn {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
        .apply-btn:hover {
            background-color: #45a049;
        }
        .stAlert {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.write(
    f"""
    <div style="text-align: center;">
        <h1 class="fade-in">Hi, {st.session_state.username}!</h1>
        <h1 class="fade-in">It's nice to see you again!</h1>
    </div>
    """, unsafe_allow_html=True
)

job_category_options = [
    "Advertising & Marketing", "Aerospace", "Agriculture", "Computer & Technology",
    "Construction", "Education", "Energy", "Entertainment", "Fashion", "Finance & Economic",
    "Food & Beverage", "Healthcare", "Hospitality", "Manufacturing", "Media & News",
    "Mining", "Pharmaceutical", "Telecommunication", "Transportation"
]

# Main function to render the app
def main():
    # Initialize the page state if not already set
    if "recruiter_home_page" not in st.session_state:
        st.session_state.recruiter_home_page = "View Jobs"
        # Page selection with proper index handling
        page = st.selectbox(
            "Select an action",
            ["View Jobs", "Add Job"],
            index=["View Jobs", "Add Job"].index(st.session_state.recruiter_home_page)
        )
        del st.session_state.recruiter_home_page
    else:
        page = st.selectbox(
            "Select an action",
            ["View Jobs", "Add Job"],
            index=["View Jobs", "Add Job"].index(st.session_state.recruiter_home_page)
        )
        del st.session_state.recruiter_home_page

    # Render the selected page
    if page == "Add Job":
        render_add_job_page()
    elif page == "View Jobs":
        render_view_jobs_page()

def render_add_job_page():
    st.header("Add a New Job")
    
    with st.form(key='add_job_form', clear_on_submit=True):
        # Fields for adding a new job
        title = st.text_input("Job Title")
        company = st.text_input("Company Name", profile.get('company_name', ''))
        location = st.text_input("Location", profile.get('office_location', ''))
        salary = st.slider("Salary (RM)", 0, 20000, step=100)
        job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Remote"])
        description = st.text_area("Job Description")
        requirements = st.text_area("Job Requirements")
        company_website = st.text_input("Company Website", profile.get('company_website', ''))
        company_contact = st.text_input("Company Contact Number", profile.get('company_contact', ''))
        benefits = st.text_area("Benefits (comma-separated)", placeholder='Parking Subsidy, Wellness Programs, etc')
        job_category = st.selectbox("Job Category", job_category_options)
        visibility = st.checkbox("Make Job Visible")
        
        submit_button = st.form_submit_button(label='Add Job')

    if submit_button:
        benefits_list = benefits.split(",") if benefits else []
        edit_flag = True
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
                job_id = insert_job(
                    user_id=profile.get('user_id'), 
                    title=title, 
                    company=company, 
                    location=location, 
                    salary=salary, 
                    job_type=job_type, 
                    description=description, 
                    requirements=requirements, 
                    posted_date=datetime.datetime.now(), 
                    company_website=company_website, 
                    company_contact=company_contact, 
                    benefits=benefits_list, 
                    job_category=job_category, 
                    visibility=visibility
                )
                st.success(f"Job '{title}' added successfully!")

def render_view_jobs_page():
    delete_flag = False
    st.header("View Jobs of Your Company")
    recruiter_id = profile.get('user_id')
    jobs = fetch_specific_jobs(recruiter_id)
    
    if not jobs:
        st.write("No jobs found.")
        return

    # Fetch the number of applications for each job
    job_ids = [job['job_id'] for job in jobs]
    application_counts = fetch_job_application_counts(job_ids)  # Fetch application counts

    # Convert jobs to DataFrame
    df = pd.DataFrame(jobs)

    # Convert application_counts dictionary to DataFrame
    application_counts_df = pd.DataFrame(list(application_counts.items()), columns=['job_id', 'application_count'])

    # Merge application counts into the DataFrame
    df = df.merge(application_counts_df, on='job_id', how='left')

    # Ensure benefits are treated as strings before applying set operations
    df['benefits'] = df['benefits'].apply(lambda x: ', '.join(set(map(str, x))) if x else '')

    # Group by unique job identifiers and aggregate the benefits
    aggregated_df = df.groupby(
        ['job_id', 'title', 'company', 'location', 'salary', 'job_type', 'description', 'requirements', 'posted_date', 'company_website', 'company_contact', 'job_category', 'visibility', 'application_count']
    ).agg({
        'benefits': 'first'
    }).reset_index()

    # Display each job using an expander
    for index, row in aggregated_df.iterrows():
        posted_date = convert_to_malaysia_time(row['posted_date'])

        with st.expander(f"{row['title'].title()}"):
            st.markdown(f"""
                <div style="padding: 10px; border: 1px solid #e6e6e6; border-radius: 10px;">
                    <h3 style="margin-bottom: 5px;">{row['title'].title()}</h3>
                    <p><strong>Company:</strong> {row['company']}</p>
                    <p><strong>Location:</strong> {row['location']}</p>
                    <p><strong>Salary (RM):</strong> {row['salary']}</p>
                    <p><strong>Job Type:</strong> {row['job_type']}</p>
                    <p><strong>Description:</strong> {row['description']}</p>
                    <p><strong>Requirements:</strong> {row['requirements']}</p>
                    <p><strong>Posted Date:</strong> {posted_date}</p>
                    <p><strong>Company Website:</strong> {row['company_website']}</p>
                    <p><strong>Company Contact:</strong> {row['company_contact']}</p>
                    <p><strong>Benefits:</strong> {row['benefits']}</p>
                    <p><strong>Job Category:</strong> {row['job_category']}</p>
                    <p><strong>Visibility:</strong> {'Visible' if row['visibility'] else 'Hidden'}</p>
                    <p><strong>Applications Received:</strong> {row['application_count']}</p>  <!-- Display application count -->
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button(f"Edit Job", key=f"edit_{index}"):
                    st.session_state.selected_job_id = row['job_id']  # Store the selected job ID
                    st.switch_page("pages/jobs_edit.py")
                    
            with col2:
                if st.button(f"Delete Job", key=f"delete_{index}"):
                    st.session_state.selected_job_id = row['job_id']  # Store the selected job ID
                    delete_job(st.session_state.selected_job_id)  # Delete the job
                    delete_flag = True
            with col3:
                if st.button(f"View Applications", key=f"view_{index}"):
                    st.session_state.selected_job_id = row['job_id']
                    st.switch_page("pages/jobs_view_applications.py")
            if delete_flag:
                st.success(f"Job '{row['title'].title()}' deleted successfully!")
                sleep(0.5)
                st.rerun()  # Trigger a rerun to refresh the job list


# Run the app
if __name__ == "__main__":
    main()
