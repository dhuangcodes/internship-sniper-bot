import requests
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
TARGET_URLS = [
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md",
    "https://raw.githubusercontent.com/codicate/underclassmen-internships/main/README.md",
    "https://raw.githubusercontent.com/northwesternfintech/2026QuantInternships/main/README.md",
    "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/main/README.md"
]

# The "Signal" keywords we are hunting for
KEYWORDS = [
    "Freshman",
    "First Year",
    "1st Year",
    "Early",
    "Discovery",
    "Summit",
    "Insight",
    "Explore",
    "2026", "Summit", "Insight", "Discovery", "Exploratory", "Fellowship", "Leadership", "Conference", "Preview", # Catch early 2026 posts
]

# File to store jobs we've already seen so we don't get spammed
HISTORY_FILE = "seen_jobs.txt"

def fetch_raw_data(url):
    """Fetches the raw text from the GitHub repository."""
    print(f"[*] Connecting to target: {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise error if website is down
        return response.text
    except Exception as e:
        print(f"[!] Error fetching data: {e}")
        return None

def parse_and_filter(raw_text, keywords):
    """
    Splits the text into lines and looks for keywords.
    Returns a list of matching lines (job postings).
    """
    matches = []
    lines = raw_text.split('\n')
    
    print(f"[*] Scanning {len(lines)} lines of data...")
    
    for line in lines:
        # We only care about table rows (which usually contain '|')
        if "|" in line:
            # Check if any of our keywords are in this line (case insensitive)
            line_lower = line.lower()
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    # Clean up the line a bit
                    clean_line = line.strip()
                    matches.append(clean_line)
                    break # Found a keyword, move to next line
    return matches

def load_history():
    """Loads the list of jobs we have already seen."""
    if not os.path.exists(HISTORY_FILE):
        return set()
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        # Read lines and remove whitespace
        return set(line.strip() for line in f)

def update_history(new_jobs):
    """Saves new jobs to our history file."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for job in new_jobs:
            f.write(job + "\n")

def run_sniper():
    print(f"\n--- INTERNSHIP SNIPER STARTED at {datetime.now()} ---")
    
    seen_jobs = load_history()
    all_new_jobs = []

    # Loop through ALL the URLs
    for url in TARGET_URLS:
        print(f"Scanning: {url}...")
        raw_text = fetch_raw_data(url)
        
        if raw_text:
            matches = parse_and_filter(raw_text, KEYWORDS)
            for job in matches:
                if job not in seen_jobs:
                    all_new_jobs.append(job)
    
    if all_new_jobs:
        print(f"\n🎯 BOOM! Found {len(all_new_jobs)} NEW opportunities.")
        
        # 1. Send the email FIRST
        send_email_alert(all_new_jobs)
        
        # 2. Then update history
        update_history(all_new_jobs)
    else:
        print(f"\nzzz... No new freshman/early programs found.")

if __name__ == "__main__":
    run_sniper()
