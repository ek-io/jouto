import yaml
import time
import os
from playwright.sync_api import sync_playwright

def get_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.yaml")

def load_config():
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        return {"personal_details": {}, "target_titles": [], "work_history": [], "education": [], "skills": [], "resume_path": ""}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}

def apply_to_job(job_url):
    config = load_config()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print(f"Navigating to {job_url}")
        page.goto(job_url)
        
        try:
            page.fill("input[name*='first_name'], input[name*='firstName']", config['personal_details']['first_name'], timeout=2000)
        except: pass
        try:
            page.fill("input[name*='last_name'], input[name*='lastName']", config['personal_details']['last_name'], timeout=2000)
        except: pass
        try:
            page.fill("input[name*='email']", config['personal_details']['email'], timeout=2000)
        except: pass
        try:
            page.fill("input[name*='phone']", config['personal_details']['phone'], timeout=2000)
        except: pass
        
        try:
            resume_path = config.get("resume_path", "resume.pdf")
            page.set_input_files("input[type='file']", resume_path, timeout=3000)
            print("Uploaded resume.")
        except:
            print("Could not find resume upload field or resume file missing.")
            
        print("Filled basic fields. Pausing for manual review before submission...")
        page.pause()
        browser.close()

if __name__ == "__main__":
    apply_to_job("https://example.com/apply")
