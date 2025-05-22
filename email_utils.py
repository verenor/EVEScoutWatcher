import os
import logging
from email.mime.text import MIMEText
from smtplib import SMTP


def send_email(subject, body):
    """Send an email notification."""
    # Retrieve email credentials from environment variables
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT", email_user)
    try:
        if not email_user or not email_pass:
            raise Exception(
                "Email credentials are missing. Please set them in the .env file."
            )

        # Set up the SMTP server
        with SMTP("smtp.gmail.com", 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(email_user, email_pass)

            # Create the email
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = email_user
            msg["To"] = recipient

            # Send the email
            server.sendmail(email_user, recipient, msg.as_string())
            logging.info("[+] Email sent successfully.")
    except Exception as e:
        logging.error(f"[!] Failed to send email: {e}")
