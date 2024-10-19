from navigation import make_sidebar
import pandas as pd
import pickle
import streamlit as st
from dependencies import insert_application, fetch_job_seeker_profile, fetch_jobs, fetch_job_seekers, fetch_applications
from time import sleep
from datetime import datetime

make_sidebar()

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "apply_message" not in st.session_state:
    st.session_state.apply_message = None

profile = fetch_job_seeker_profile(st.session_state.user_id)

# Custom CSS for enhanced styling and fade-in effect
st.markdown("""
    <style>
        .fade-in {
            animation: fadeIn 1s ease-in-out;
        }

        .fade-in-slow {
            animation: fadeIn 2s ease-in-out;
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
            color: white;
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
        .title-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .recommendations-header {
            text-align: center;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

def save_apply(job_title, company, job_seeker_id, recruiter_id, job_id):
    apply_message = insert_application(job_seeker_id, recruiter_id, job_id)
    if apply_message == "Application already exists.":
        st.session_state.apply_message = "Application already exists. ❌"
    else:
        st.session_state.apply_message = f"You have applied for the position of {job_title} at {company if company else 'the company'}! 🚀"
    st.session_state.last_applied_job = job_title

def get_recommendations_userwise(user_id, user_based_df, user_based_cosine_sim):
    user_index = user_based_df[user_based_df['user_id'] == user_id].index[0]
    sim_scores = list(enumerate(user_based_cosine_sim[user_index]))
    user_list = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    similar_users = user_based_df.iloc[[i[0] for i in user_list]]['user_id'].tolist()
    return similar_users

def show_job_recommendations():
    jobs_list = fetch_jobs()
    application_list = fetch_applications()

    jobs = pd.DataFrame(jobs_list)
    applications = pd.DataFrame(application_list)

    user_based_df = pickle.load(open('user_based_jobrec.pkl', 'rb'))
    user_based_cosine_sim = pickle.load(open('user_based_similarities.pkl', 'rb'))

    similar_users = get_recommendations_userwise(profile['user_id'], user_based_df, user_based_cosine_sim)
    similar_user_applications = applications[applications['job_seeker_id'].isin(similar_users)]
    recommended_jobs = jobs[jobs['job_id'].isin(similar_user_applications['job_id'].unique())]
    recommended_jobs = recommended_jobs.sample(frac=1)
    job_count = 0
    for index, job in recommended_jobs.iterrows():
        if job['visibility'] and job_count < 10:
            job_count += 1
            posted_date = job.get('posted_date')
            posted_date = datetime.fromisoformat(str(posted_date)).strftime('%Y-%m-%d')

            with st.expander(f"{index + 1}. {job['title'].title()} - {job['location']} 🌍"):
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
                if st.button(f"Apply for {job['title'].title()} 📝", key=f"apply_{index}", on_click=save_apply, args=(job['title'], job.get('company', None), profile.get('user_id'), job.get('user_id'), job.get('job_id'))):
                    pass
                
                if st.session_state.apply_message and st.session_state.last_applied_job == job['title']:
                    if st.session_state.apply_message == "Application already exists. ❌":
                        st.error(st.session_state.apply_message)
                    else:
                        st.success(st.session_state.apply_message)

if __name__ == '__main__':
    st.markdown(f"""
        <div class="title-container">
            <h1 class="fade-in">User-Based Job Recommendation</h1>
            <h2 class="fade-in-slow">Here are the 10 jobs recommended to you based on users similar to your profile!</h2>
        </div>
    """, unsafe_allow_html=True)
    
    show_job_recommendations()
