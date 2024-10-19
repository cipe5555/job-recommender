from navigation import make_sidebar
import streamlit as st
from dependencies import fetch_job_seeker_profile, update_job_seeker_profile, validate_username, validate_phone, validate_email, get_user_emails, get_user_phones, update_user_profile, fetch_user
from datetime import date
from time import sleep

make_sidebar()

if "user_id" not in st.session_state and not st.session_state.get("jobseeker_logged_in", False):
    st.error("Please log in to view your profile.")
    st.stop()

def save_profile():
    profile_data = {
        "full_name": full_name,
        "phone": phone,
        "email": email,
        "current_job_title": current_job_title,
        "current_employer": current_employer,
        "years_of_experience": years_of_experience,
        "skills": skills.split(','),
        "professional_summary": professional_summary,
        "linkedin_profile": linkedin_profile,
        "personal_website": personal_website,
        "education": [
            {
                "education_level": education_level,
                "major": major,
                "institution": institution,
                "graduation_year": graduation_year
            }
        ],
        "preferences": {
            "desired_job_title": desired_job_title,
            "preferred_industries": preferred_industries,
            "salary_expectations": salary_expectations,
            "work_type_preference": work_type_preference
        },
    }
    update_job_seeker_profile(st.session_state.user_id, profile_data)
    update_user_profile(st.session_state.user_id, users_data)

    st.session_state.username = full_name
    st.success("Profile updated successfully! 🎉")
    sleep(0.5)
    st.rerun()

profile = fetch_job_seeker_profile(st.session_state.user_id)
user = fetch_user(st.session_state.user_id)

current_date = date.today()
current_year = current_date.year

major_options = ['', "Pre-University Programme", "Accounting & Finance", "Agriculture, Forestry, Fusgery & Veterinary",
                 "Architecture & Building", "Arts & Design", "Audio-visual Techniques & Media Production",
                 "Business Management & Administration", "Computing & IT", "Communication & Broadcasting",
                 "Education", "Engineering & Engineering Trades", "Environmental Protection",
                 "Hospitality & Tourism", "Humanities", "Languages", "Law", "Manufacturing & Processing",
                 "Marketing & Sales", "Mathematics & Statistics", "Medical Diagnostic & Treatment Technology",
                 "Medicine & Healthcare", "Occupational Health & Hygiene Services", "Personal Services",
                 "Science (Life Science/Physical Science/Applied Science)", "Security Services",
                 "Social Sciences", "Social Services", "Transport Services"]
years_of_experience_options = ['', "0-2 years", "3-5 years", "6-10 years", "10+ years"]
education_level_options = ['', "None", "High School", "Vocational", "Associate's", "Bachelor's", "Master's", "PhD"]
years_options = list(range(1970, int(current_year) + 1))[::-1]
preferred_industries_options = ['', "Advertising & Marketing", "Aerospace", "Agriculture", "Computer & Technology",
                                "Construction", "Education", "Energy", "Entertainment", "Fashion", "Finance & Economic",
                                "Food & Beverage", "Healthcare", "Hospitality", "Manufacturing", "Media & News",
                                "Mining", "Pharmaceutical", "Telecommunication", "Transportation"]
work_type_preference_options = ['', "Full-time", "Part-time", "Remote", "Contract"]

st.markdown("""
    <style>
        .profile-title {
            color: #4CAF50;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
        }
        .profile-subheader {
            color: white;
            font-size: 24px;
            margin-top: 20px;
        }
        .profile-section {
            margin-bottom: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
        .profile-section h3 {
            color: #4CAF50;
        }
        .profile-input {
            margin-bottom: 10px;
        }
        .stAlert {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

if profile:
    st.markdown("<h1 class='profile-title'>Profile 📄</h1>", unsafe_allow_html=True)
    st.write("")
    
    st.markdown("<h2 class='profile-subheader'>Basic Info</h2>", unsafe_allow_html=True)

    full_name = st.text_input("Full Name", profile.get('full_name', ''), key='full_name', help="Enter your full name")
    phone = st.text_input("Phone", profile.get('phone', ''), key='phone', help="Enter your phone number")
    email = st.text_input("Email", profile.get('email', ''), key='email', help="Enter your email address")
    password = st.text_input("New Password", type="password", key='password', help="Enter a new password if you want to change it")

    st.markdown("</div>", unsafe_allow_html=True)

    users_data = {
        "username": full_name,
        "phone": phone,
        "email": email,
        "password": password
    }
    edit_flag = True

    st.markdown("<h2 class='profile-subheader'>Professional Information</h2>", unsafe_allow_html=True)

    current_job_title = st.text_input("Current Job Title", profile.get('current_job_title', ''), key='current_job_title', help="Enter your current job title")
    current_employer = st.text_input("Current Employer", profile.get('current_employer', ''), key='current_employer', help="Enter your current employer")
    years_of_experience = profile.get('years_of_experience', '0-2 years')
    if years_of_experience not in years_of_experience_options:
        years_of_experience = '0-2 years'
    years_of_experience = st.selectbox("Years of Experience", years_of_experience_options, index=years_of_experience_options.index(years_of_experience), key='years_of_experience', help="Select your years of experience")
    skills = st.text_area("Skills (comma-separated)", ','.join(profile.get('skills', [])), placeholder="python,data mining,etc", key='skills', help="Enter your skills, separated by commas")
    professional_summary = st.text_area("Professional Summary", profile.get('professional_summary', ''), key='professional_summary', help="Enter a brief professional summary")
    linkedin_profile = st.text_input("LinkedIn Profile URL", profile.get('linkedin_profile', ''), key='linkedin_profile', help="Enter your LinkedIn profile URL")
    personal_website = st.text_input("Personal Website URL", profile.get('personal_website', ''), key='personal_website', help="Enter your personal website URL")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h2 class='profile-subheader'>Educational Background</h2>", unsafe_allow_html=True)

    education = profile.get('education', [{}])[0]
    education_level = st.selectbox("Highest Education Level", education_level_options, index=education_level_options.index(education.get('education_level', "Bachelor's")), key='education_level', help="Select your highest education level")
    major = st.selectbox("Major", major_options, index=major_options.index(education.get('major', 'Other')), key='major', help="Select your major")
    institution = st.text_input("Institution Name", education.get('institution', ''), key='institution', help="Enter the name of your institution")
    graduation_year = education.get('graduation_year', int(current_year)+1)
    if graduation_year not in years_options:
        graduation_year = int(current_year)
    graduation_year = st.selectbox("Graduation Year", years_options, index=years_options.index(graduation_year), key='graduation_year', help="Select your graduation year")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h2 class='profile-subheader'>Preferences</h2>", unsafe_allow_html=True)

    preferences = profile.get('preferences', {})
    desired_job_title = st.text_input("Desired Job Title", preferences.get('desired_job_title', ''), key='desired_job_title', help="Enter your desired job title")
    preferred_industries = st.multiselect("Preferred Industries", preferred_industries_options, preferences.get('preferred_industries', []), key='preferred_industries', help="Select your preferred industries")
    salary_expectations = st.slider("Monthly Salary Expectation (RM)", 0, 20000, preferences.get('salary_expectations', 3000), 100, key='salary_expectations', help="Select your monthly salary expectation")
    work_type_preference = st.multiselect("Work Type Preference", work_type_preference_options, preferences.get('work_type_preference', []), key='work_type_preference', help="Select your work type preference")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Save Profile"):
        if full_name != profile.get('full_name'):
            if not validate_username(full_name) or not full_name:
                st.warning('Invalid Name')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["username"] = full_name

        if phone != profile.get('phone'):
            if not validate_phone(phone):
                st.warning('Invalid Phone Number')
                sleep(0.5)
                edit_flag = False
            elif phone in get_user_phones():
                st.warning('Phone Number already exists')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["phone"] = phone

        if email != profile.get('email'):
            if not validate_email(email):
                st.warning('Invalid Email Address')
                sleep(0.5)
                edit_flag = False
            elif email in get_user_emails():
                st.warning('Email Address already exists')
                sleep(0.5)
                edit_flag = False
            else:
                users_data["email"] = email
        if not password:
            users_data["password"] = user.get('password')

        elif password:
            if len(password) < 6 or not password:
                st.warning("Password is Too Short (Minimum 6 characters)")
                sleep(0.5)
                edit_flag = False
            else:
                users_data["password"] = password

        if edit_flag:
            save_profile()
        else:
            st.rerun()

else:
    st.error("Unable to fetch profile information. Please try again later.")
