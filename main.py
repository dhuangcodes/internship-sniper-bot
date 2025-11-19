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

# Updated Keywords (Broader to catch more finance roles)
KEYWORDS = [
    "Freshman", "First Year", "Sophomore", "Discovery", "Summit", "Insight", "Explore", 
    "Quantitative", "Trader", "Analyst", "Finance", "Business", "2026"
]

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
HISTORY_FILE = "seen_jobs.txt"

def fetch_raw_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200: return response.text
    except: pass
    return None

def parse_and_filter(raw_text, keywords):
    matches = []
    lines = raw_text.split('\n')
    for line in lines:
        # Look for lines that are table rows (|) and contain a keyword
        if "|" in line and "---" not in line:
            line_lower = line.lower()
            if any(k.lower() in line_lower for k in keywords):
                # Clean up the line to make it readable
                clean_line = line.replace("|", " ").strip()
                matches.append(clean_line)
    return matches

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r") as f: return set(line.strip() for line in f)

def update_history(new_jobs):
    with open(HISTORY_FILE, "a") as f:
        for job in new_jobs: f.write(job + "\n")

def send_html_email(new_jobs):
    msg = EmailMessage()
    msg['Subject'] = f"🎯 Sniper Alert: {len(new_jobs)} New Opportunities!"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # Create a nice HTML table
    html_content = f"""
    <html>
      <body>
        <h2>🚀 Found {len(new_jobs)} New Jobs</h2>
        <table style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Job Details</th>
          </tr>
          {''.join([f'<tr><td style="padding: 8px; border-bottom: 1px solid #ddd;">{job}</td></tr>' for job in new_jobs])}
        </table>
        <p>Good luck! - Your Python Bot</p>
      </body>
    </html>
    """
    msg.set_content("New jobs found (view as HTML).")
    msg.add_alternative(html_content, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

def run_sniper():
    print("Checking for internships...")
    seen_jobs = load_history()
    all_new_jobs = []

    for url in TARGET_URLS:
        text = fetch_raw_data(url)
        if text:
            matches = parse_and_filter(text, KEYWORDS)
            for job in matches:
                if job not in seen_jobs:
                    all_new_jobs.append(job)

    if all_new_jobs:
        print(f"Found {len(all_new_jobs)} new jobs. Sending email...")
        send_html_email(all_new_jobs)
        update_history(all_new_jobs)
    else:
        print("No new jobs found.")

if __name__ == "__main__":
    run_sniper()
