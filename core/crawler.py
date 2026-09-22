import os
import sqlite3
import urllib.request
import xml.etree.ElementTree as ET
import time
from database import add_global_job

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
            description = item.findtext('description')
            
            # Simple heuristic to extract company if available (e.g., "Software Engineer at Google")
            company = "Unknown"
            if " at " in title:
                parts = title.split(" at ")
                title = parts[0]
                company = parts[1].split(" (")[0] # Remove location parens if present
                
            if title and link:
                add_global_job(title=title, url=link, company=company, snippet=description[:500], source=source_name)
                count += 1
                
        print(f"Successfully ingested {count} jobs from {source_name}")
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")

def run_crawler():
    # List of free public job RSS feeds
    rss_feeds = [
        ("https://weworkremotely.com/remote-jobs.rss", "WeWorkRemotely"),
        ("https://remoteok.com/remote-jobs.rss", "RemoteOK"),
        ("https://remotive.com/api/remote-jobs?format=rss", "Remotive")
    ]
    
    while True:
        print("\n--- Starting crawler loop ---")
        for url, name in rss_feeds:
            fetch_rss_jobs(url, name)
            time.sleep(2) # Polite delay between sources
            
        print("Crawler sleeping for 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    run_crawler()
