from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_job_seeker_profile, search_jobs, insert_application
from datetime import datetime

make_sidebar()

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "page" not in st.session_state:
    st.session_state.page = 0

if "apply_message" not in st.session_state:
    st.session_state.apply_message = None

if "last_search_query" not in st.session_state:
    st.session_state.last_search_query = ""

if "last_applied_job" not in st.session_state:
    st.session_state.last_applied_job = ""

def save_apply(job_title, company, job_seeker_id, recruiter_id, job_id):
    apply_message = insert_application(job_seeker_id, recruiter_id, job_id)
    if apply_message == "Application already exists.":
        st.session_state.apply_message = "Application already exists. ❌"
    else:
        st.session_state.apply_message = f"You have applied for the position of {job_title} at {company if company else 'the company'}! 🚀"
    st.session_state.last_applied_job = job_title

# Custom CSS for fade-in effect and enhanced UI
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
        .job-card {
            padding: 20px;
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            background-color: #c0c0c0;
            margin-bottom: 20px;
        }
        .job-card h3 {
            margin-bottom: 5px;
            color: #4CAF50;
        }
        .job-card p {
            margin: 5px 0;
            color: #333;
        }
        .stMarkdown h3, .stMarkdown p, .stMarkdown subheader {
            color: #333 !important;
        }
        .page-navigation {
            margin-top: 20px;
            text-align: center;
        }
        .stAlert {
            text-align: center;
        }
        .no-matching-jobs {
            color: white;
            text-align: center;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

profile = fetch_job_seeker_profile(st.session_state.user_id)
preferences = profile.get('preferences', {})

def job_search_page():
    st.title('Job Search 🔍')
    
    search_query = st.text_input('Search for jobs by title:', key='search_query', help="Enter job title")

    if search_query:
        if search_query != st.session_state.last_search_query:
            st.session_state.page = 0
            st.session_state.apply_message = None
            st.session_state.last_search_query = search_query
        
        matching_jobs = search_jobs(search_query.lower())
        if matching_jobs:
            jobs_per_page = 10
            total_jobs = len(matching_jobs)
            total_pages = (total_jobs + jobs_per_page - 1) // jobs_per_page
            start_index = st.session_state.page * jobs_per_page
            end_index = start_index + jobs_per_page
            displayed_jobs = matching_jobs[start_index:end_index]
            job_count = 0

            for idx, job in enumerate(displayed_jobs, start=1):
                if job['visibility'] and job_count < 10:
                    posted_date = job.get('posted_date')
                    posted_date = datetime.fromisoformat(str(posted_date)).strftime('%Y-%m-%d')
                    
                    with st.expander(f"{idx}. {job['title'].title()} - {job['location']} 🌍"):
                        st.markdown(f"""
                            <div class="job-card fade-in">
                                <h3>{job['title'].title()} - {job['location']}</h3>
                                <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                                <p><strong>Location:</strong> {job['location']}</p>
                                <p><strong>Salary (RM):</strong> {job['salary']}</p>
                                <p><strong>Description:</strong> <br>{job['description']}</p>
                                <p><strong>Requirements:</strong> <br>{job['requirements']}</p>
                                <p><strong>Date Posted:</strong> {posted_date if posted_date else 'N/A'}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.write("")
                        if st.button(f"Apply for {job['title'].title()} 📝", key=f"apply_{start_index + idx}", on_click=save_apply, args=(job['title'], job.get('company', None), profile.get('user_id'), job.get('user_id'), job.get('job_id'))):
                            pass
                        
                        if st.session_state.apply_message and st.session_state.last_applied_job == job['title']:
                            if st.session_state.apply_message == "Application already exists. ❌":
                                st.error(st.session_state.apply_message)
                            else:
                                st.success(st.session_state.apply_message)

            st.markdown('<div class="page-navigation">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Previous ⬅️"):
                    if st.session_state.page > 0:
                        st.session_state.page -= 1
            with col3:
                if st.button("Next ➡️"):
                    if st.session_state.page < total_pages - 1:
                        st.session_state.page += 1
            st.markdown('</div>', unsafe_allow_html=True)
            st.write(f"Page {st.session_state.page + 1} of {total_pages}")
        else:
            st.markdown('<div class="no-matching-jobs">No matching jobs found. 😔</div>', unsafe_allow_html=True)
        del st.session_state.apply_message

if __name__ == '__main__':
    job_search_page()
