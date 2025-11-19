import requests
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

# --- CONFIGURATION ---
TARGET_URLS = [
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md",
    "https://raw.githubusercontent.com/codicate/underclassmen-internships/main/README.md",
    "https://raw.githubusercontent.com/northwesternfintech/2026QuantInternships/main/README.md"
]

# KEYWORDS to search for
KEYWORDS = [
    "Freshman", "First Year", "1st Year", "Early", 
    "Discovery", "Summit", "Insight", "Explore", "2026",
    "Quantitative", "Trader", "Analyst", "Product", "Data", "Finance", "Business",
    "Goldman", "Sachs", "Morgan", "Stanley", "Chase", "Capital One"
]

# Credentials from GitHub Secrets
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

HISTORY_FILE = "seen_jobs.txt"

def fetch_raw_data(url):
    """Fetches the raw text from the GitHub repository."""
    print(f"[*] Connecting to target: {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[!] Error fetching data: {e}")
        return None

def parse_and_filter(raw_text, keywords):
    """Scans text for keywords."""
    matches = []
    lines = raw_text.split('\n')
    print(f"[*] Scanning {len(lines)} lines of data...")
    
    for line in lines:
        if "|" in line:
            line_lower = line.lower()
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    matches.append(line.strip())
                    break 
    return matches

def load_history():
    """Loads the list of jobs we have already seen."""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def update_history(new_jobs):
    """Updates the history file."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for job in new_jobs:
            f.write(job + "\n")

def send_email_alert(new_jobs):
    """Sends an email with the list of new jobs."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("[!] Email credentials not found. Skipping email.")
        return

    print("[*] Preparing email notification...")
    subject = f"🎯 Internship Sniper: Found {len(new_jobs)} Opportunities!"
    
    # Build the email body
    body = "The bot found the following new freshman/sophomore programs:\n\n"
    for job in new_jobs:
        body += f"- {job}\n"
    body += "\nGood luck!\n- Your Python Bot"

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("[+] Email sent successfully!")
    except Exception as e:
        print(f"[!] Failed to send email: {e}")

def run_sniper():
    print(f"\n--- INTERNSHIP SNIPER STARTED at {datetime.now()} ---")
    
    seen_jobs = load_history()
    all_new_jobs = []

    # Loop through ALL the URLs
    for url in TARGET_URLS:
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
