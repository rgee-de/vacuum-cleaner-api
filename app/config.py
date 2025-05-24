import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Roborock credentials
ROBOROCK_USER = os.getenv("ROBOROCK_USER")
ROBOROCK_PASSWORD = os.getenv("ROBOROCK_PASSWORD")

# Logging level configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Allowed WebSocket origins (comma-separated in .env)
ORIGINS = os.getenv("ORIGINS").split(",")

# WebSocket connection URL
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")

# Coordinates for cleaning task
CLEANING_X = int(os.getenv("CLEANING_X"))
CLEANING_Y = int(os.getenv("CLEANING_Y"))
