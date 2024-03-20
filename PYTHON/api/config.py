from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

class Settings(BaseSettings):
    # success: bool = load_dotenv()
    # if not success:
    #     print('Error loading env')
    DATABASE_URI: str = "mariadb+mariadbconnector://rob@localhost:3306/scribe"
    try:
        smtp_server: str = os.environ.get("SMTP_SERVER")
        smtp_port: str = os.environ.get("SMTP_PORT")
        smtp_username: str = os.environ.get("SMTP_USERNAME")
        password: str = os.environ.get("SMTP_PASSWORD")
        FRONTEND_URL: str = os.environ.get("FRONTEND_URL")
        DATABASE_URI: str = f'{os.environ.get("DATABASE_CONNECTOR")}://{os.environ.get("MYSQL_USER")}:{os.environ.get("MYSQL_PASSWORD")}@scribe_db:3306/{os.environ.get("MYSQL_DATABASE")}'
        print(f'env vars: {smtp_server}\n{smtp_port}\n{FRONTEND_URL}')
    except Exception as e:
        print(f"[ERROR]: Failed to get credentials from SMTP environment vars. This script cannot continue. Please make sure you have SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD set.\nOutput: {str(e)}")
        quit()

    print(f'Database uri: {DATABASE_URI}')

    # print(f"SMTP server: {smtp_server}")
    # print(f"SMTP port: {smtp_port}")
    # print(f"SMTP username: {username}")
    # print(f"SMTP password: {password}")

settings = Settings()

