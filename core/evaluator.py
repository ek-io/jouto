import os
import yaml
import json
import google.generativeai as genai

def get_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.yaml")

def load_config():
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        return {"personal_details": {}, "target_titles": [], "work_history": [], "education": [], "skills": [], "resume_path": ""}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}

def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def evaluate_job(job_snippet, job_title, config):
    model = get_model()
    if not model:
        return {"score": 0, "reasoning": "GEMINI_API_KEY environment variable not set."}
    
    prompt = f"""
    Evaluate the following job opportunity based on the applicant's profile.
    
    Applicant Profile:
    {yaml.dump(config)}
    
    Job Title: {job_title}
    Job Description/Snippet:
    {job_snippet}
    
    Based on the skills, experience, and target titles, provide a fit score out of 100 and a brief reasoning (1-2 sentences).
    Format the response EXACTLY as a JSON object:
    {{"score": 85, "reasoning": "Strong match with Python and SQL skills."}}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        return {"score": 0, "reasoning": f"Error evaluating job: {e}"}

def generate_cover_letter(job_snippet, job_title, config):
    model = get_model()
    if not model:
        return "GEMINI_API_KEY not set. Cannot generate cover letter."
    
    prompt = f"""
    Write a concise, professional cover letter for the following job opportunity based on the applicant's profile.
    Keep it under 3 paragraphs. Focus on the most relevant skills. Do not include placeholder addresses.
    
    Applicant Profile:
    {yaml.dump(config)}
    
    Job Title: {job_title}
    Job Description/Snippet:
    {job_snippet}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating cover letter: {e}"

if __name__ == "__main__":
    config = load_config()
    res = evaluate_job("Looking for a Data Analyst with 2 years of SQL and Python experience to build dashboards.", "Data Analyst", config)
    print(res)
