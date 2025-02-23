import os

from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ORIGINS = os.getenv("ORIGINS").split(",")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")

CLEANING_X = int(os.getenv("CLEANING_X"))
CLEANING_Y = int(os.getenv("CLEANING_Y"))
