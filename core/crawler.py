import os
import json
import urllib.request
import xml.etree.ElementTree as ET
import time
from database import add_global_job

def is_indian_job(title, company, text):
    content = (f"{title} {company} {text}").lower()
    indian_keywords = [
        "india", "bangalore", "bengaluru", "mumbai", "pune", 
        "hyderabad", "delhi", "gurgaon", "noida", "chennai", 
        "ahmedabad", "kolkata"
    ]
    return any(keyword in content for keyword in indian_keywords)

def fetch_rss_jobs(feed_url, source_name):
    print(f"Fetching jobs from {source_name} RSS feed...")
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        count = 0
        for item in root.findall('.//item'):
            title = item.findtext('title')
            link = item.findtext('link')
            description = item.findtext('description') or ""
            
            company = "Unknown"
            if " at " in title:
                parts = title.split(" at ")
                title = parts[0]
                company = parts[1].split(" (")[0]
                
            if title and link:
                if is_indian_job(title, company, description):
                    add_global_job(title=title, url=link, company=company, snippet=description[:500], source=source_name)
                    count += 1
                
        print(f"Successfully ingested {count} Indian jobs from {source_name}")
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")

def fetch_arbeitnow_jobs():
    print("Fetching jobs from Arbeitnow API...")
    try:
        req = urllib.request.Request("https://www.arbeitnow.com/api/job-board-api", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            
        count = 0
        for job in data.get('data', []):
            title = job.get('title')
            company = job.get('company_name')
            link = job.get('url')
            description = job.get('description', '')
            
            if title and link:
                if is_indian_job(title, company, description):
                    add_global_job(title=title, url=link, company=company, snippet=description[:500], source="Arbeitnow")
                    count += 1
                
        print(f"Successfully ingested {count} Indian jobs from Arbeitnow")
    except Exception as e:
        print(f"Error fetching Arbeitnow: {e}")

def fetch_hn_jobs():
    print("Fetching jobs from Hacker News (YCombinator)...")
    try:
        # Get latest job story IDs
        req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/jobstories.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            job_ids = json.loads(response.read())
            
        count = 0
        # Only process top 30 to prevent rate limiting
        for job_id in job_ids[:30]:
            try:
                item_req = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{job_id}.json", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(item_req) as item_resp:
                    job = json.loads(item_resp.read())
                    
                if not job: continue
                
                title = job.get('title', '')
                link = job.get('url', f"https://news.ycombinator.com/item?id={job_id}")
                text = job.get('text', '')
                
                # HN jobs often format title as "Company is hiring Role"
                company = "YCombinator Startup"
                if " is hiring " in title:
                    parts = title.split(" is hiring ")
                    company = parts[0]
                    title = parts[1]
                elif " (" in title:
                    company = title.split(" (")[0]
                    
                if title:
                    if is_indian_job(title, company, text):
                        add_global_job(title=title, url=link, company=company, snippet=text[:500], source="Hacker News")
                        count += 1
                time.sleep(0.5) # Polite delay for HN API
            except:
                pass
                
        print(f"Successfully ingested {count} Indian jobs from Hacker News")
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")

def run_crawler():
    rss_feeds = [
        ("https://weworkremotely.com/remote-jobs.rss", "WeWorkRemotely"),
        ("https://weworkremotely.com/categories/remote-programming-jobs.rss", "WWR Programming"),
        ("https://remoteok.com/remote-jobs.rss", "RemoteOK"),
        ("https://remotive.com/api/remote-jobs?format=rss", "Remotive")
    ]
    
    while True:
        print("\n--- Starting crawler loop ---")
        
        # 1. RSS Feeds
        for url, name in rss_feeds:
            fetch_rss_jobs(url, name)
            time.sleep(2)
            
        # 2. Arbeitnow API
        fetch_arbeitnow_jobs()
        time.sleep(2)
        
        # 3. Hacker News API
        fetch_hn_jobs()
        
        print("Crawler sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    run_crawler()
