import yaml
import os
from duckduckgo_search import DDGS

def get_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.yaml")

def load_config():
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        return {"personal_details": {}, "target_titles": [], "work_history": [], "education": [], "skills": [], "resume_path": ""}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}

def discover_jobs(titles, platforms=["site:greenhouse.io", "site:lever.co"]):
    results = []
    with DDGS() as ddgs:
        for title in titles:
            for platform in platforms:
                query = f'{platform} "{title}"'
                print(f"Searching: {query}")
                search_results = ddgs.text(query, max_results=10)
                if search_results:
                    for r in search_results:
                        results.append({
                            "title": r.get('title', ''),
                            "url": r.get('href', ''),
                            "snippet": r.get('body', ''),
                            "query": query
                        })
    return results

if __name__ == "__main__":
    config = load_config()
    titles = config.get("target_titles", [])
    jobs = discover_jobs(titles)
    for j in jobs:
        print(j['title'], j['url'])
