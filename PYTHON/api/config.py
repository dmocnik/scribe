from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from smtp.smtp_module import scribe_smtp
import os

class Settings(BaseSettings):
    load_dotenv()
    DATABASE_URI: str = "mariadb+mariadbconnector://rob@localhost:3306/scribe"
    try:
        smtp_server: str = os.environ.get("SMTP_SERVER")
        smtp_port: str = os.environ.get("SMTP_PORT")
        smtp_username: str = os.environ.get("SMTP_USERNAME")
        password: str = os.environ.get("SMTP_PASSWORD")
    except Exception as e:
        print(f"[ERROR]: Failed to get credentials from SMTP environment vars. This script cannot continue. Please make sure you have SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD set.\nOutput: {str(e)}")
        quit()

    # print(f"SMTP server: {smtp_server}")
    # print(f"SMTP port: {smtp_port}")
    # print(f"SMTP username: {username}")
    # print(f"SMTP password: {password}")

settings = Settings()

