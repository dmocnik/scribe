# MIT License
# Copyright (c) 2024

# [ Check out the `usage.py` file for an example, as well as ``../../DOCS/SMTP Class.md` for documentation! ]

# Attempt to import all necessary libraries
try:
    import os # General
    import smtplib # SMTP
    from email.mime.text import MIMEText # Email ASCII
    from rich import print as rich_print # Pretty print
    from rich.traceback import install # Pretty traceback
    install() # Install traceback
except ImportError as e:
    print("[INFO] You are missing one or more libraries. Please use PIP to install any missing ones.")
    print("Try running `python3 -m pip install -r ../../requirements.txt`")
    print(f"Traceback: {e}")
    quit()

# Determine the main project directory, for compatibility (the absolute path to this file)
maindirectory = os.path.join(os.path.dirname(os.path.abspath(__file__))) 

# Class to send emails using SMTP
class scribe_smtp:
    def __init__(self, smtp_server, smtp_port, username, password):
        print("[INFO] Initializing SMTP server...")
        # Set vars
        self.smtp_server = str(smtp_server)
        self.smtp_port = int(smtp_port)
        self.username = str(username)
        self.password = str(password)
        # Try to login to the SMTP server
        try:
            print(f"[INFO] Logging in to SMTP server {self.smtp_server}:{self.smtp_port} as {self.username}...")
            self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            self.server.login(self.username, self.password)
        except Exception as e:
            print(f"[ERROR] Failed to initialize SMTP server. Output: {str(e)}")
            return False
        # Show init message
        print(f"SMTP server initialized successfully on {self.smtp_server}:{self.smtp_port}")

    def send_template(self, to, subject, template, data={}):
        # Send an email using one of our template files
        # Read the template file
        try:
            with open(os.path.join(maindirectory, "templates", f"{template}"), "r") as f:
                template_text = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read template file. Output: {str(e)}")
            return False
        # Replace the placeholder tags in the template with the data. Placeholders are in the format {{key}}.
        for key in data:
            template_text = template_text.replace(f"{{{{{key}}}}}", data[key])
        # Create a MIMEText object for compatibility
        message = MIMEText(template_text, "html")
        message["Subject"] = subject
        message["From"] = self.username
        message["To"] = to
        # Send the email
        try:
            self.server.send_message(message)
        except Exception as e:
            print(f"[ERROR] Failed to send email. Output: {str(e)}")
            return False
        # Show success message
        print(f"Email sent successfully to {to}.")
        return True

    def send_email(self, to, subject, body):
        # Send an email using a subject and body
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = self.username
        message["To"] = to
        # Send the email
        try:
            self.server.send_message(message)
        except Exception as e:
            print(f"[ERROR] Failed to send email. Output: {str(e)}")
            return False
        # Show success message
        print(f"Email sent successfully to {to}.")
        return True
    
    def shutdown(self):
        # Shutdown the SMTP server if it exists
        if self.server:
            try:
                self.server.quit()
            except Exception as e:
                print(f"[ERROR] Failed to shutdown SMTP server. Output: {str(e)}")
                return False
        # Show success message
        print(f"SMTP server shutdown successfully.")
        return True
    
    def __del__(self):
        # Shutdown the SMTP server when the class is deleted
        self.shutdown()
