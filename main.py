import requests
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
# The RAW URL of the markdown file we want to scrape.
# (Using the PittCSC Summer 2025 list as a test bed, since 2026 is just starting)
TARGET_URL = "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/main/README.md"

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
    
    # 1. Load History
    seen_jobs = load_history()
    
    # 2. Fetch Data
    raw_text = fetch_raw_data(TARGET_URL)
    if not raw_text:
        return

    # 3. Find all relevant jobs (Freshman/Sophomore focus)
    all_matches = parse_and_filter(raw_text, KEYWORDS)
    
    # 4. Filter for ONLY new ones
    new_discoveries = []
    for job in all_matches:
        if job not in seen_jobs:
            new_discoveries.append(job)
    
    # 5. Report Results
    if new_discoveries:
        print(f"\n🎯 BOOM! Found {len(new_discoveries)} NEW opportunities:\n")
        for job in new_discoveries:
            print(f"   > {job}")
        
        # Save to history so we don't see them again next time
        update_history(new_discoveries)
    else:
        print(f"\nzzz... No new freshman/early programs found. Scanned {len(all_matches)} existing matches.")

if __name__ == "__main__":
    run_sniper()
