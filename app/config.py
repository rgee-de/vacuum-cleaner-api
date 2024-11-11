import os

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ORIGINS = os.getenv("ORIGINS").split(",")
