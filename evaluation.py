import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score
import warnings
import pickle
import gc
import logging
from dependencies import fetch_job_seekers, fetch_jobs, fetch_applications


def evaluate_recommendations(recommended_titles, true_titles, top_n=10):
    all_recommended = []
    all_true = []

    for rec_titles in recommended_titles:
        all_recommended.extend(rec_titles[:top_n])
        all_true.extend(true_titles)

    all_recommended = list(set(all_recommended))
    true_titles_set = set(true_titles)

    true_labels = [1 if title in true_titles_set else 0 for title in all_recommended]
    true_labels_binary = [1]*len(true_titles) + [0]*(len(all_recommended) - len(true_titles))

    precision = precision_score(true_labels_binary, true_labels, average='micro')
    recall = recall_score(true_labels_binary, true_labels, average='micro')
    f1 = f1_score(true_labels_binary, true_labels, average='micro')

    average_precision = average_precision_score(true_labels_binary, true_labels)

    return precision, recall, f1, average_precision

def evaluate_user_recommendations(recommended_users, true_user_ids, top_n=10):
    all_recommended = []
    all_true = []

    for rec_users in recommended_users:
        all_recommended.extend(rec_users[:top_n])
        all_true.extend(true_user_ids)

    all_recommended = list(set(all_recommended))
    true_user_ids_set = set(true_user_ids)

    true_labels = [1 if user in true_user_ids_set else 0 for user in all_recommended]
    true_labels_binary = [1]*len(true_user_ids) + [0]*(len(all_recommended) - len(true_user_ids))

    precision = precision_score(true_labels_binary, true_labels, average='micro')
    recall = recall_score(true_labels_binary, true_labels, average='micro')
    f1 = f1_score(true_labels_binary, true_labels, average='micro')

    average_precision = average_precision_score(true_labels_binary, true_labels)

    return precision, recall, f1, average_precision

def get_recommendations(title, jobs, indices, cosine_sim):
    idx = indices.get(title, None)
    if idx is None:
        # print(f"Title '{title}' not found in indices.")
        return []
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    job_indices = [i[0] for i in sim_scores]
    
    valid_indices = [i for i in job_indices if i < len(jobs)]
    
    return jobs['title'].iloc[valid_indices].tolist()

def get_recommendations_userwise(user_id, job_seekers_indices, user_based_cosine_sim, job_seekers_df):
    idx = job_seekers_indices.get(user_id, None)
    if idx is None:
        print(f"User ID '{user_id}' not found in indices.")
        return []
    sim_scores = list(enumerate(user_based_cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    job_seeker_indices = [i[0] for i in sim_scores]
    similar_user_ids = job_seekers_df.loc[job_seeker_indices, 'user_id'].tolist()
    return similar_user_ids[0:16]

def get_job_recommendations_for_seeker(seeker_profile, jobs, tfidf_vectorizer, tfidf_matrix):
    # Transform the job seeker's profile into TF-IDF matrix using the same vectorizer
    seeker_profile_tfidf = tfidf_vectorizer.transform([seeker_profile])
    
    # Compute cosine similarity between the job seeker profile and job postings
    similarity_scores = linear_kernel(seeker_profile_tfidf, tfidf_matrix)
    
    # Get the job indices sorted by similarity score
    job_indices = similarity_scores[0].argsort()[::-1]

    # Fetch the job titles 
    recommended_jobs = jobs.iloc[job_indices]['title'].tolist()[:16]
    
    return recommended_jobs

def evaluate_profile_based_recommendations(job_seekers, jobs, tfidf_vectorizer, tfidf_matrix, top_n=10):
    recommended_titles = []
    true_titles = []

    for _, seeker in job_seekers.iterrows():
        profile = seeker['training']
        true_job_titles = seeker['applied_jobs']

        recommended_jobs = get_job_recommendations_for_seeker(profile, jobs, tfidf_vectorizer, tfidf_matrix)
        recommended_titles.append(recommended_jobs[:top_n])
        true_titles.extend(true_job_titles)
    
    precision, recall, f1, average_precision = evaluate_recommendations(recommended_titles, true_titles)
    return precision, recall, f1, average_precision


def main():
    warnings.simplefilter('ignore')

    # Configure logging
    logging.basicConfig(filename='evaluation_results.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Load job data
    jobs_list = fetch_jobs()
    jobs = pd.DataFrame(jobs_list)

    # Fill missing values
    jobs['title'] = jobs['title'].fillna('')
    jobs['description'] = jobs['description'].fillna('')
    jobs['requirements'] = jobs['requirements'].fillna('')
    jobs['job_category'] = jobs['job_category'].fillna('')

    # Make a new column for training
    jobs['training'] = jobs['title'] + jobs['description'] + jobs['requirements'] + jobs['job_category']

    # Create TF-IDF matrix
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.01, stop_words='english')
    tfidf_matrix = tf.fit_transform(jobs['training'])

    # Compute cosine similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Reset index and prepare indices
    jobs = jobs.reset_index()
    titles = jobs['title']
    indices = pd.Series(jobs.index, index=jobs['title'])

    # Save the models
    pickle.dump(jobs, open('jobrec.pkl', 'wb'))
    pickle.dump(cosine_sim, open('similarities.pkl', 'wb'))

    # Clean up
    gc.collect()

    # Load job seeker and application data
    job_seeker_list = fetch_job_seekers()
    application_list = fetch_applications()

    job_seekers = pd.DataFrame(job_seeker_list)
    applications = pd.DataFrame(application_list)

    # Fill NaN values for scalar columns
    job_seekers['current_job_title'] = job_seekers['current_job_title'].fillna('')
    job_seekers['current_employer'] = job_seekers['current_employer'].fillna('')
    job_seekers['years_of_experience'] = job_seekers['years_of_experience'].fillna(0)
    job_seekers['professional_summary'] = job_seekers['professional_summary'].fillna('')
    job_seekers['linkedin_profile'] = job_seekers['linkedin_profile'].fillna('')
    job_seekers['personal_website'] = job_seekers['personal_website'].fillna('')

    # Fill NaN values for list columns
    job_seekers['skills'] = job_seekers['skills'].apply(lambda x: x if isinstance(x, list) else [])
    job_seekers['education'] = job_seekers['education'].apply(lambda x: x if isinstance(x, list) else [{
        'education_level': '',
        'major': '',
        'institution': '',
        'graduation_year': ''
    }])
    job_seekers['preferences'] = job_seekers['preferences'].apply(lambda x: x if isinstance(x, dict) else {
        'desired_job_title': '',
        'preferred_industries': [],
        'salary_expectations': 0,
        'work_type_preference': []
    })

    # Convert lists to strings for concatenation
    job_seekers['skills_str'] = job_seekers['skills'].apply(lambda x: ' '.join(x))
    job_seekers['preferred_industries_str'] = job_seekers['preferences'].apply(lambda x: ' '.join(x.get('preferred_industries', [])))

    job_seekers['training'] = (
        job_seekers['current_job_title'] + " " +
        job_seekers['preferences'].apply(lambda x: x.get('desired_job_title', '')) + " " +
        job_seekers['preferred_industries_str'] + " " +
        job_seekers['skills_str'] + " " +
        job_seekers['education'].apply(lambda x: x[0].get('major', '') if x else '') + " " +
        job_seekers['professional_summary']
    )

    job_seekers['applied_jobs'] = job_seekers['user_id'].apply(
        lambda user_id : applications[applications['job_seeker_id'] == user_id]['job_id'].tolist()
    )

    # Create TF-IDF matrix for user profiles
    user_based_tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.01, stop_words='english')
    user_based_tfidf_matrix = user_based_tf.fit_transform(job_seekers['training'])
    user_based_cosine_sim = linear_kernel(user_based_tfidf_matrix, user_based_tfidf_matrix)

    job_seekers_df = job_seekers.reset_index()
    job_seekers_indices = pd.Series(job_seekers_df.index, index=job_seekers_df['user_id'])

    # Save the models
    pickle.dump(job_seekers_df, open('user_based_jobrec.pkl', 'wb'))
    pickle.dump(user_based_cosine_sim, open('user_based_similarities.pkl', 'wb'))

    # Split data for evaluation
    jobs_train, jobs_test = train_test_split(jobs, test_size=0.2, random_state=42)
    job_seekers_train, job_seekers_test = train_test_split(job_seekers, test_size=0.2, random_state=42)

    # Evaluate profile-based job recommendations
    precision, recall, f1, average_precision = evaluate_profile_based_recommendations(job_seekers_test, jobs, tf, tfidf_matrix)
    logging.info(f"Profile-based Precision: {precision}, Recall: {recall}, F1 Score: {f1}, Average Precision: {average_precision}")
    # print(f"Profile-based Precision: {precision}, Recall: {recall}, F1 Score: {f1}, Average Precision: {average_precision}")

    # Evaluate job recommendations
    test_titles = jobs_test['title'].tolist()
    recommended_titles = [get_recommendations(title, jobs_train, indices, cosine_sim) for title in test_titles]
    true_titles = jobs_test['title'].tolist()

    precision, recall, f1, map_score = evaluate_recommendations(recommended_titles, true_titles, top_n=10)
    logging.info(f"Job Similarities-based Model - Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}, MAP: {map_score:.4f}")
    # print(f"Job Similarities-based Model - Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}, MAP: {map_score:.4f}")

    # Evaluate user recommendations
    test_user_ids = job_seekers_test['user_id'].tolist()
    recommended_users = [get_recommendations_userwise(user_id, job_seekers_indices, user_based_cosine_sim, job_seekers_df) for user_id in test_user_ids]
    true_user_ids = job_seekers_test['user_id'].tolist()

    precision, recall, f1, map_score = evaluate_user_recommendations(recommended_users, true_user_ids, top_n=10)
    logging.info(f"User Profile Similarities-based Model - Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}, MAP: {map_score:.4f}")
    # print(f"User Profile Similarities-based Model - Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}, MAP: {map_score:.4f}")

if __name__ == "__main__":
    main()