import smtplib
import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# GitHub Environment Variables
GITHUB_REPO = os.getenv('GITHUB_REPOSITORY')
GITHUB_RUN_ID = os.getenv('GITHUB_RUN_ID')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO')
SMTP_SERVER = os.getenv('SMTP_SERVER', "smtp.gmail.com")
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

print("Here is the run id: ",GITHUB_RUN_ID)
# GitHub API URL to fetch workflow job details
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{GITHUB_RUN_ID}/jobs"
print("Result of API Call: ", API_URL)

# Headers for API authentication
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Function to fetch failed jobs
def get_failed_jobs():
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        jobs = response.json().get("jobs", [])
        error_logs = ""
        for job in jobs:
            if job["conclusion"] == "failure":
                error_logs += f"❌ **Job Failed**: {job['name']}\n"
                for step in job["steps"]:
                    if step["conclusion"] == "failure":
                        error_logs += f"   ⚠️ **Step**: {step['name']} - {step['conclusion']}\n"
        return error_logs if error_logs else None
    else:
        return f"Error fetching workflow details: {response.text}"

# Function to send failure email
def send_email(error_logs):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"🚨 GitHub Workflow Failed: {GITHUB_REPO}"

    body = f"""
    🚨 **GitHub Actions Workflow Failed!** 🚨
    🔹 **Repository**: {GITHUB_REPO}
    🔹 **Workflow Run ID**: {GITHUB_RUN_ID}
    
    **Failure Details:**  
    {error_logs}

    👉 View Workflow Logs: [Click Here](https://github.com/{GITHUB_REPO}/actions/runs/{GITHUB_RUN_ID})
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_TO.split(","), msg.as_string())
        server.quit()
        print("✅ Failure email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")

# Run the script
error_logs = get_failed_jobs()
if error_logs:
    send_email(error_logs)
else:
    print("✅ No failures detected, no email sent.")
