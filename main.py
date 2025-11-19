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

KEYWORDS = [
    "Freshman", "First Year", "1st Year", "Sophomore", 
    "Discovery", "Summit", "Insight", "Explore", "Fellowship",
    "Quantitative", "Trader", "Analyst", "Product", "Data", "Finance", "Business", "Strategy",
    "2026", "Goldman", "Sachs", "Morgan", "Stanley", "JPMorgan", "Chase", 
    "Bank of America", "Citi", "Citigroup", "Wells Fargo", "Barclays","Deloitte", "PwC", "KPMG", "EY", "Ernst", 
    "McKinsey", "Bain", "BCG", "Google", "Microsoft", "Meta", "Facebook", "Uber","BlackRock", "Blackstone", "Citadel", "Two Sigma", "Jane Street", 
    "DE Shaw", "Hudson River Trading", "Point72",
]

# Words that mean "Don't show me this"
BAD_KEYWORDS = [
    "Closed", "🔒", "❌", "No longer accepting"
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
        if "|" in line and "---" not in line:
            line_lower = line.lower()
            
            # 1. Check for GOOD keywords
            if any(k.lower() in line_lower for k in keywords):
                
                # 2. Check for BAD keywords (Filter out closed jobs)
                if not any(b.lower() in line_lower for b in BAD_KEYWORDS):
                    
                    # Clean up the line
                    clean_line = line.replace("|", " ").strip()
                    matches.append(clean_line)
    return matches

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r") as f: return set(line.strip() for line in f)

def update_history(new_jobs):
    with open(HISTORY_FILE, "a") as f:
        for job in new_jobs: f.write(job + "\n")

def send_email_alert(new_jobs, nothing_found=False):
    msg = EmailMessage()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    if nothing_found:
        current_day = datetime.now().strftime('%A')
        msg['Subject'] = f"📉 Internship Sniper: Nothing New ({current_day})"
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2>It's {current_day}, but nothing new has dropped.</h2>
            <p>No new <strong>open</strong> freshman/sophomore internships were found today.</p>
            <p><strong>Recommendation:</strong> Go grind some LeetCode or work on your projects!</p>
            <br>
            <p>- Your Python Bot</p>
          </body>
        </html>
        """
        msg.set_content(f"It's {current_day}, but nothing new has dropped.")
        msg.add_alternative(body, subtype='html')
    else:
        msg['Subject'] = f"🎯 Sniper Alert: {len(new_jobs)} New OPEN Opportunities!"
        
        rows = ""
        for job in new_jobs:
            rows += f"<tr><td style='padding: 10px; border-bottom: 1px solid #ddd;'>{job}</td></tr>"

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2e6c80;">🚀 Found {len(new_jobs)} New OPEN Jobs</h2>
            <table style="border-collapse: collapse; width: 100%; max-width: 800px;">
              <tr style="background-color: #f2f2f2;">
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Job Details</th>
              </tr>
              {rows}
            </table>
            <p style="margin-top: 20px;">Good luck! - Your Python Bot</p>
          </body>
        </html>
        """
        msg.set_content("New jobs found.")
        msg.add_alternative(html_content, subtype='html')

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("[+] Email sent successfully!")
    except Exception as e:
        print(f"[!] Failed to send email: {e}")

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
        send_email_alert(all_new_jobs)
        update_history(all_new_jobs)
    else:
        print("No new jobs found. Sending 'Grind LeetCode' email...")
        send_email_alert([], nothing_found=True)

if __name__ == "__main__":
    run_sniper()
