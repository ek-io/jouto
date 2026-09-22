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

def apply_to_job(job_url, user_profile, bulk_mode=False):
    config = user_profile
    
    with sync_playwright() as p:
        # Run headless in bulk mode for speed and stability
        browser = p.chromium.launch(headless=bulk_mode)
        page = browser.new_page()
        print(f"Navigating to {job_url}")
        
        try:
            page.goto(job_url, timeout=30000)
            
            try:
                page.fill("input[name*='first_name'], input[name*='firstName']", config['personal_details'].get('first_name', ''), timeout=2000)
            except: pass
            try:
                page.fill("input[name*='last_name'], input[name*='lastName']", config['personal_details'].get('last_name', ''), timeout=2000)
            except: pass
            try:
                page.fill("input[name*='email']", config['personal_details'].get('email', ''), timeout=2000)
            except: pass
            try:
                page.fill("input[name*='phone']", config['personal_details'].get('phone', ''), timeout=2000)
            except: pass
            
            try:
                resume_bytes = config.get('resume_file')
                resume_name = config.get('resume_name', 'resume.pdf')
                if resume_bytes:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(resume_bytes)
                        tmp_path = tmp.name
                        
                    page.set_input_files("input[type='file']", tmp_path, timeout=3000)
                    print("Uploaded resume from cloud.")
                    os.unlink(tmp_path)
            except Exception as e:
                print(f"Could not upload resume: {e}")
                
            if not bulk_mode:
                print("Filled basic fields. Pausing for manual review before submission...")
                page.pause()
            else:
                print("Bulk Mode active. Attempting to click submit (simulated).")
                # In a real scenario, we would find the submit button and click it:
                # try: page.click("button[type='submit']") except: pass
                # For safety in this demo, we just wait a second
                time.sleep(1)
                
        except Exception as e:
            print(f"Failed to apply to {job_url}: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    apply_to_job("https://example.com/apply")
