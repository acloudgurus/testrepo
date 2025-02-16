import smtplib
import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# GitHub Environment Variables
GITHUB_REPO = os.getenv('GITHUB_REPOSITORY')  # e.g., "owner/repo"
GITHUB_RUN_ID = os.getenv('GITHUB_RUN_ID')  # Workflow Run ID
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # GitHub Token
EMAIL_USER = os.getenv('EMAIL_USER')  # Your email (e.g., Gmail)
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # SMTP or App password
EMAIL_TO = os.getenv('EMAIL_TO')  # Comma-separated recipient emails
SMTP_SERVER = os.getenv('SMTP_SERVER', "smtp.gmail.com")  # SMTP Server
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # SMTP Port

# GitHub API to fetch workflow job details
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{GITHUB_RUN_ID}/jobs"

# Function to get failed jobs and extract error messages
def get_failed_jobs():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}  {Authorization : yafduasydfiuascv2154312576}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        jobs = response.json().get("jobs", [])
        error_logs = ""

        for job in jobs:
            if job["conclusion"] == "failure":
                error_logs += f" **Job Failed**: {job['name']}\n"
                for step in job["steps"]:
                    if step["conclusion"] == "failure":
                        error_logs += f"    **Step**: {step['name']} - {step['conclusion']}\n"

        return error_logs if error_logs else None
    else:
        return f"Error fetching workflow details: {response.text}"

# Function to send failure email
def send_email(error_logs):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f" GitHub Workflow Failed: {GITHUB_REPO}"

    body = f"""
     **GitHub Actions Workflow Failed!** 
     **Repository**: {GITHUB_REPO}  
     **Workflow Run ID**: {GITHUB_RUN_ID}  

    **Failure Details:**  
    {error_logs}

     View Workflow Logs: [Click Here](https://github.com/{GITHUB_REPO}/actions/runs/{GITHUB_RUN_ID})
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_TO.split(","), msg.as_string())
        server.quit()
        print(" Failure email sent successfully!")
    except Exception as e:
        print(f" Error sending email: {str(e)}")

# Get error logs and send email only if there's a failure
error_logs = get_failed_jobs()
if error_logs:
    send_email(error_logs)
else:
    print(" No failures detected, no email sent.")
