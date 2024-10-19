from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from dependencies import fetch_jobs, fetch_job_seeker_profile, insert_application
import streamlit as st
from navigation import make_sidebar
from datetime import datetime

make_sidebar()

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "apply_message" not in st.session_state:
    st.session_state.apply_message = None

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
    </style>
""", unsafe_allow_html=True)

def save_apply(job_title, company, job_seeker_id, recruiter_id, job_id):
    apply_message = insert_application(job_seeker_id, recruiter_id, job_id)
    if apply_message == "Application already exists.":
        st.session_state.apply_message = "Application already exists. ❌"
    else:
        st.session_state.apply_message = f"You have applied for the position of {job_title} at {company if company else 'the company'}! 🚀"
    st.session_state.last_applied_job = job_title

def get_job_recommendations_for_seeker(seeker_profile, jobs, tfidf_vectorizer, tfidf_matrix):
    # Transform the job seeker's profile into TF-IDF matrix using the same vectorizer
    seeker_profile_tfidf = tfidf_vectorizer.transform([seeker_profile])
    
    # Compute cosine similarity between the job seeker profile and job postings
    similarity_scores = linear_kernel(seeker_profile_tfidf, tfidf_matrix)
    
    # Get the job indices sorted by similarity score
    job_indices = similarity_scores[0].argsort()[::-1]

    # Fetch all job information based on top N indices
    recommended_jobs = jobs.iloc[job_indices].to_dict('records')
    
    return recommended_jobs

def show_job_recommendation():

    job_seeker = fetch_job_seeker_profile(st.session_state.user_id)
    jobs_list = fetch_jobs()
    jobs = pd.DataFrame(jobs_list)

    # Fill missing values
    jobs['title'] = jobs['title'].fillna('')
    jobs['description'] = jobs['description'].fillna('')
    jobs['requirements'] = jobs['requirements'].fillna('')
    jobs['job_category'] = jobs['job_category'].fillna('')
    
    # Prepare training data for job postings
    jobs['training'] = jobs['title'] + " " + jobs['description'] + " " + jobs['requirements'] + " " + jobs['job_category']

    job_seeker = pd.DataFrame([job_seeker])

    # Fill NaN values for scalar columns
    job_seeker['current_job_title'] = job_seeker['current_job_title'].fillna('')
    job_seeker['current_employer'] = job_seeker['current_employer'].fillna('')
    job_seeker['years_of_experience'] = job_seeker['years_of_experience'].fillna(0)
    job_seeker['professional_summary'] = job_seeker['professional_summary'].fillna('')
    job_seeker['linkedin_profile'] = job_seeker['linkedin_profile'].fillna('')
    job_seeker['personal_website'] = job_seeker['personal_website'].fillna('')

    # Fill NaN values for list columns
    job_seeker['skills'] = job_seeker['skills'].apply(lambda x: x if isinstance(x, list) else [])
    job_seeker['education'] = job_seeker['education'].apply(lambda x: x if isinstance(x, list) else [{
        'education_level': '',
        'major': '',
        'institution': '',
        'graduation_year': ''
    }])
    job_seeker['preferences'] = job_seeker['preferences'].apply(lambda x: x if isinstance(x, dict) else {
        'desired_job_title': '',
        'preferred_industries': [],
        'salary_expectations': 0,
        'work_type_preference': []
    })

    job_seeker['skills_str'] = job_seeker['skills'].apply(lambda x: ' '.join(x))
    job_seeker['preferred_industries_str'] = job_seeker['preferences'].apply(lambda x: ' '.join(x.get('preferred_industries', [])))
    job_seeker['training'] = (
        job_seeker['current_job_title'] + " " +
        job_seeker['preferences'].apply(lambda x: x.get('desired_job_title', '')) + " " +
        job_seeker['preferred_industries_str'] + " " +
        job_seeker['skills_str'] + " " +
        job_seeker['education'].apply(lambda x: x[0].get('major', '') if x else '') + " " +
        job_seeker['professional_summary']
    )

    tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.01, stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(jobs['training'])

    # Get job recommendations for the job seeker
    recommended_jobs = get_job_recommendations_for_seeker(job_seeker['training'][0], jobs, tfidf_vectorizer, tfidf_matrix)
    recommended_jobs = pd.DataFrame(recommended_jobs)
    
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
                if st.button(f"Apply for {job['title'].title()} 📝", key=f"apply_{index}", on_click=save_apply, args=(job['title'], job.get('company', None), job_seeker['user_id'][0], job.get('user_id'), job.get('job_id'))):
                    pass
                
                if st.session_state.apply_message and st.session_state.last_applied_job == job['title']:
                    if st.session_state.apply_message == "Application already exists. ❌":
                        st.error(st.session_state.apply_message)
                    else:
                        st.success(st.session_state.apply_message)

if __name__ == "__main__":
    st.write(f"""
        <div class="title-container">
            <h1 class="fade-in">Profile-Based Job Recommendation</h1>
            <h2 class="fade-in-slow">Here are the top 10 jobs recommended to you based on your profile!</h2>
        </div>
    """, unsafe_allow_html=True)

    show_job_recommendation()
