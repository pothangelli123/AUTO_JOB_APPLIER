from flask import Flask, render_template, request, redirect, url_for
import yaml
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('resume_form.html')

@app.route('/submit_resume', methods=['POST'])
def submit_resume():
    form_data = request.form

    # Process multiple entries (experience, projects, achievements, languages)
    def process_multiple_entries(prefix):
        entries = []
        i = 0
        while f'{prefix}_{i}_name' in form_data:
            entry = {key.replace(f'{prefix}_{i}_', ''): form_data[key] 
                     for key in form_data if key.startswith(f'{prefix}_{i}_')}
            if entry:
                # Ensure key_responsibilities and skills_acquired are lists
                if 'key_responsibilities' in entry:
                    entry['key_responsibilities'] = [{'responsibility': resp} for resp in entry['key_responsibilities'].split(',')]
                if 'skills_acquired' in entry:
                    entry['skills_acquired'] = entry['skills_acquired'].split(',')
                entries.append(entry)
            i += 1
        return entries

    # Create resume data dictionary
    resume_data = {
        'personal_information': {
            'name': form_data['name'],
            'surname': form_data['surname'],
            'date_of_birth': form_data['date_of_birth'],
            'country': form_data['country'],
            'city': form_data['city'],
            'address': form_data['address'],
            'zip_code': form_data['zip_code'],
            'phone_prefix': form_data['phone_prefix'],
            'phone': form_data['phone'],
            'email': form_data['email'],
            'github': form_data['github'],
            'linkedin': form_data['linkedin'],
        },
        'education_details': [{
            'education_level': form_data['education_level'],
            'institution': form_data['institution'],
            'field_of_study': form_data['field_of_study'],
            'final_evaluation_grade': form_data['final_evaluation_grade'],
            'start_date': form_data['start_date'],
            'year_of_completion': form_data['year_of_completion'],
            'exam': {name: grade for name, grade in zip(form_data.getlist('exam_name[]'), form_data.getlist('exam_grade[]'))}
        }],
        'experience_details': process_multiple_entries('experience'),
        'projects': process_multiple_entries('project'),
        'achievements': process_multiple_entries('achievement'),
        'languages': process_multiple_entries('language'),
        'interests': form_data['interests'].split(','),  # Convert to list
        'availability': {
            'notice_period': form_data['notice_period'],
        },
        'salary_expectations': {
            'salary_range_usd': form_data['salary_range_usd'],
        },
        'self_identification': {
            'gender': form_data['gender'],
            'pronouns': form_data['pronouns'],
            'veteran': form_data['veteran'],
            'disability': form_data['disability'],
            'ethnicity': form_data['ethnicity'],
        },
        'legal_authorization': {
            'eu_work_authorization': form_data['eu_work_authorization'],
            'us_work_authorization': form_data['us_work_authorization'],
            'requires_us_visa': form_data['requires_us_visa'],
            'requires_us_sponsorship': form_data['requires_us_sponsorship'],
            'requires_eu_visa': form_data['requires_eu_visa'],
            'legally_allowed_to_work_in_eu': form_data['legally_allowed_to_work_in_eu'],
            'legally_allowed_to_work_in_us': form_data['legally_allowed_to_work_in_us'],
            'requires_eu_sponsorship': form_data['requires_eu_sponsorship'],
            'canada_work_authorization': form_data['canada_work_authorization'],
            'requires_canada_visa': form_data['requires_canada_visa'],
            'legally_allowed_to_work_in_canada': form_data['legally_allowed_to_work_in_canada'],
            'requires_canada_sponsorship': form_data['requires_canada_sponsorship'],
            'uk_work_authorization': form_data['uk_work_authorization'],
            'requires_uk_visa': form_data['requires_uk_visa'],
            'legally_allowed_to_work_in_uk': form_data['legally_allowed_to_work_in_uk'],
            'requires_uk_sponsorship': form_data['requires_uk_sponsorship'],
        },
        'work_preferences': {
            'remote_work': form_data['remote_work'],
            'in_person_work': form_data['in_person_work'],
            'open_to_relocation': form_data['open_to_relocation'],
            'willing_to_complete_assessments': form_data['willing_to_complete_assessments'],
            'willing_to_undergo_drug_tests': form_data['willing_to_undergo_drug_tests'],
            'willing_to_undergo_background_checks': form_data['willing_to_undergo_background_checks'],
        }
    }

    # Save the resume data to the YAML file
    with open('data_folder/plain_text_resume.yaml', 'w') as file:
        yaml.dump(resume_data, file, default_flow_style=False)

    return redirect(url_for('preferences_form'))

@app.route('/preferences')
def preferences_form():
    return render_template('preferences_form.html')

@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    config_data = {
        'remote': 'remote' in request.form,
        'experienceLevel': {
            'internship': 'experienceLevel_internship' in request.form,
            'entry': 'experienceLevel_entry' in request.form,
            'associate': 'experienceLevel_associate' in request.form,
            'mid-senior level': 'experienceLevel_mid-senior' in request.form,
            'director': 'experienceLevel_director' in request.form,
            'executive': 'experienceLevel_executive' in request.form,
        },
        'jobTypes': {
            'full-time': 'jobTypes_full-time' in request.form,
            'contract': 'jobTypes_contract' in request.form,
            'part-time': 'jobTypes_part-time' in request.form,
            'temporary': 'jobTypes_temporary' in request.form,
            'internship': 'jobTypes_internship' in request.form,
            'other': 'jobTypes_other' in request.form,
            'volunteer': 'jobTypes_volunteer' in request.form,
        },
        'date': {
            'all time': 'date_all_time' in request.form,
            'month': 'date_month' in request.form,
            'week': 'date_week' in request.form,
            '24 hours': 'date_24_hours' in request.form,
        },
        'positions': request.form['positions'].split(','),
        'locations': request.form['locations'].split(','),
        'apply_once_at_company': 'apply_once_at_company' in request.form,
        'distance': int(request.form['distance']),
        'company_blacklist': request.form['company_blacklist'].split(','),
        'title_blacklist': request.form['title_blacklist'].split(','),
        'job_applicants_threshold': {
            'min_applicants': int(request.form['min_applicants']),
            'max_applicants': int(request.form['max_applicants']),
        },
        'llm_model_type': request.form['llm_model_type'],
        'llm_model': request.form['llm_model'],
        'llm_api_url': request.form['llm_api_url'],
    }
    
    # Save the config data to the YAML file
    with open('data_folder/config.yaml', 'w') as file:
        yaml.dump(config_data, file, default_flow_style=False)
    
    # Execute main.py
    subprocess.Popen(['python', 'main.py'], cwd=os.path.dirname(os.path.abspath(__file__)))
    
    return "Preferences updated and application started!"

if __name__ == '__main__':
    app.run(debug=True)