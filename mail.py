import smtplib
import os
import re
from email.message import EmailMessage

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_email(to, subject, body, tone=None):

    if not is_valid_email(to):
        return f"❌ Invalid email address: {to}"
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("YOUR_EMAIL")
    msg['To'] = to
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv("YOUR_EMAIL"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        return f"Email sent to {to} ✅"
    except Exception as e:
        return f"Failed to send email ❌: {e}"