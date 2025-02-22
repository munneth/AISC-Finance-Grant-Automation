import requests
import hashlib
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# Grant webpages to monitor
URLS = [
    "https://csi.ucdavis.edu/grants",
    "https://ccc.ucdavis.edu/grants",
    "https://ucdaviscenterforstudentinvolvement.submittable.com/submit"
]

# Email settings
SMTP_SERVER = "smtp.gmail.com"  # Change if using a different email provider
SMTP_PORT = 587
EMAIL_SENDER = "aisc.finance.ucd@gmail.com"
EMAIL_PASSWORD = "hsys vmzi maku ziyy"  # Use an app password for security
EMAIL_RECEIVER = "cgarciapablo@ucdavis.edu"

# File to store previous page hashes
HASH_FILE = "grant_page_hashes.txt"

# Load previous hashes (if any)
def load_hashes():
    try:
        with open(HASH_FILE, "r") as file:
            return {line.split()[0]: line.split()[1] for line in file.readlines()}
    except FileNotFoundError:
        return {}

# Save updated hashes
def save_hashes(hashes):
    with open(HASH_FILE, "w") as file:
        for url, hash_value in hashes.items():
            file.write(f"{url} {hash_value}\n")

# Function to fetch the webpage content and generate a hash
def get_page_hash(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract relevant text (modify this if grant listings are inside a specific <div> or <ul>)
        main_content = soup.get_text()

        return hashlib.md5(main_content.encode("utf-8")).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to send an email notification
def send_email(url):
    subject = "New Grant Posted!"
    body = f"A new grant has been posted or the webpage has been updated: {url}\nCheck it out!"
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"Email notification sent for {url}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to check for updates
def check_for_updates():
    hashes = load_hashes()
    new_hashes = {}

    for url in URLS:
        new_hash = get_page_hash(url)
        if new_hash:
            if url in hashes and hashes[url] != new_hash:
                print(f"Change detected at {url}")
                send_email(url)
            else:
                print("no change")
            new_hashes[url] = new_hash

    save_hashes(new_hashes)

# Schedule the script to run daily
schedule.every().day.at("15:53").do(check_for_updates)  # Runs daily at 8 AM

if __name__ == "__main__":
    check_for_updates()  # Run once at startup

