# [ Example usage file for scribe_smtp class ]

# MIT License
# Copyright (c) 2024


# Import the smtp class
from smtp.smtp_module import scribe_smtp

# Load vars from .env file in the current directory
from dotenv import load_dotenv
load_dotenv()

# Get SMTP server credentials from environment vars (for docker)
import os
try:
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
except Exception as e:
    print(f"[ERROR]: Failed to get credentials from SMTP environment vars. This script cannot continue. Please make sure you have SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD set.\nOutput: {str(e)}")
    quit()

print(f"SMTP server: {smtp_server}")
print(f"SMTP port: {smtp_port}")
print(f"SMTP username: {username}")
print(f"SMTP password: {password}")

# Create an instance of the scribe_smtp class with the credentials
smtp_driver = scribe_smtp(smtp_server, smtp_port, username, password)

# Example email
# smtp_driver.send_template(to='john@example.com', subject='Server Test', template='example.html', data={'name': 'John', 'link': 'http://example.com'})
# Account verification email
# smtp_driver.send_template(to='john@example.com', subject='Welcome! Verify your Scribe Account', template='verify_account.html', data={'name': 'John', 'verification_link': 'http://example.com/verify.php?token=1234567890'})
# Password reset email
# smtp_driver.send_template(to='john@example.com', subject='Scribe Password Reset', template='password_reset.html', data={'name': 'John', 'reset_link': 'http://example.com/reset.php?id=1234567890'})
# Stupid email
smtp_driver.send_template(to='robertquigley@oakland.edu', subject='Bruh', template='foot.html')

# Garbage collection (calls shutdown method)
del smtp_driver
