from navigation import make_sidebar
import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
from dependencies import insert_application, fetch_job_seeker_profile
from time import sleep

make_sidebar()

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "home_apply_message" not in st.session_state:
    st.session_state.home_apply_message = None

if "last_applied_job" not in st.session_state:
    st.session_state.last_applied_job = ""

if "selected_job_name" not in st.session_state:
    st.session_state.selected_job_name = ""

profile = fetch_job_seeker_profile(st.session_state.user_id)

# Custom CSS for enhanced styling and fade-in effect
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
        .title-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .stMarkdown h3, .stMarkdown p, .stMarkdown subheader {
            color: #333 !important;
        }
        .recommendations-header {
            text-align: center;
            margin: 20px 0;
        }
        .stAlert {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

def get_recommendations(title, jobs, indices, cosine_sim):
    job_index = jobs[jobs['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[job_index]))
    job_list = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]
    recommended_jobs = [jobs.iloc[i[0]] for i in job_list]
    return recommended_jobs

def save_apply(job_title, company, job_seeker_id, recruiter_id, job_id):
    apply_message = insert_application(job_seeker_id, recruiter_id, job_id)
    if apply_message == "Application already exists.":
        st.session_state.home_apply_message = "Application already exists. ❌"
    else:
        st.session_state.home_apply_message = f"You have applied for the position of {job_title} at {company if company else 'the company'}! 🚀"
    st.session_state.last_applied_job = job_title

def show_job_recommendations():
    st.subheader("📈 Let Us Recommend You Some Jobs")

    # Load the data and similarity matrix
    jobs = pickle.load(open('jobrec.pkl', 'rb'))
    cosine_sim = pickle.load(open('similarities.pkl', 'rb'))

    job_titles = jobs['title'].str.title()

    # Prepare indices
    indices = pd.Series(jobs.index, index=jobs['title'])

    if "selected_job_name" not in st.session_state or not st.session_state.selected_job_name:
        selected_job_name = st.selectbox('🔍 Select a job you like to find', job_titles.values, help="Choose a job title that you are interested in.")
        if st.button('Recommend'):
            st.session_state.selected_job_name = selected_job_name
            st.session_state.recommended_jobs = get_recommendations(st.session_state.selected_job_name.lower(), jobs, indices, cosine_sim)
            st.session_state.show_recommendations = True
            st.rerun()

    if "show_recommendations" in st.session_state and st.session_state.show_recommendations:
        selected_job_name = st.selectbox('🔍 Select a job you like to find', job_titles.values, help="Choose a job title that you are interested in.")
        if st.button('Recommend'):
            st.session_state.selected_job_name = selected_job_name
            st.session_state.recommended_jobs = get_recommendations(st.session_state.selected_job_name.lower(), jobs, indices, cosine_sim)
            st.session_state.show_recommendations = True
        st.subheader("📋 Here are the top 10 recommended jobs you may be interested in!")
        job_count = 0
        for idx, job in enumerate(st.session_state.recommended_jobs):
            if job['visibility'] and job_count<10:
                job_count+=1
                posted_date = job.get('posted_date')
                posted_date = datetime.fromisoformat(str(posted_date)).strftime('%Y-%m-%d')
                
                with st.expander(f"{job['title'].title()} - {job['location']} 🌍"):
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

                    if st.session_state.home_apply_message and st.session_state.last_applied_job == job['title']:
                        if st.session_state.home_apply_message == "Application already exists. ❌":
                            st.error(st.session_state.home_apply_message)
                        else:
                            st.success(st.session_state.home_apply_message)
                    if st.button(f"Apply for {job['title'].title()} 📝", key=f"apply_{idx}", on_click=save_apply, args=(job['title'], job.get('company', None), profile.get('user_id'), job.get('user_id'), job.get('job_id'))):
                        st.session_state.last_applied_job = job['title'].title()
                        sleep(1.5)
                        st.experimental_rerun()

if __name__ == '__main__':
    st.markdown(f"""
        <div class="title-container">
            <h1 class="fade-in">Hi, {st.session_state.username}! 👋</h1>
            <h2 class="fade-in">Welcome back! Here's what we have for you today.</h2>
        </div>
    """, unsafe_allow_html=True)
    
    show_job_recommendations()
