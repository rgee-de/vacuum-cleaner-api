# README for Roborock Vacuum-Cleaner API

A lightweight FastAPI service that exposes a REST interface for controlling your Roborock vacuum‑cleaner via the
community python‑roborock library.

## Table of Contents

- [Requirements](#requirements)
- [Setup and Configuration](#setup-and-configuration)
    - [Environment Variables](#environment-variables)
    - [Running the Docker Container](#running-the-docker-container)
    - [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
    - [Control Endpoints](#control-endpoints)
- [Project Structure](#project-structure)
- [Additional Information](#additional-information)

## Requirements

- Python 3.10 or higher
- A Roborock cloud account (e‑mail & password)
- Docker
- The dependencies listed in requirements.txt—most importantly
    - fastapi
    - uvicorn (for local development)
    - python‑dotenv
    - python‑roborock

## Setup and Configuration

### Environment Variables

Change the .env file in the root directory

- ROBOROCK_USER: Roborock cloud e‑mail account
- ROBOROCK_PASSWORD: Roborock cloud password
- LOG_LEVEL: The logging level (ERROR or INFO).
- ORIGINS: CORS Origins.
- WEBSOCKET_URL: URL where the server runs.
- CLEANING_X, CLEANING_Y: Maintenance coordinates for the POST /goto/maintenance route

### Running the Docker Container

1. Build the image

```powershell
docker build -t vacuum-cleaner-api .
```

2. Start the container (loads variables from your .env):

```powershell
docker run --env-file .env -p 8000:8000 vacuum-cleaner-api
```

### Running the Application

For a local development workflow without Docker:

```powershell
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Control Endpoints

- GET /prop: Retrieve the full DeviceProp object reported by the robot
- GET /rooms: List all rooms with cleaning statistics
- GET /modes: Show every predefined cleaning mode and its parameters
- POST /clean/settings: Persist new default CleaningSettings
- POST /clean/segments: Start a cleaning task for one or more segment IDs
- POST /goto/maintenance: Drive the robot to the configured maintenance point
- POST /goto/charge: Send the robot back to the dock
- POST /stop: Stop the current task immediately
- POST /pause: Pause the current task

## Project Structure

 ```text
app/
├─ config.py           # Loads environment variables
├─ main.py             # FastAPI application & dependency wiring
├─ model/              # Pydantic schemas (CleaningSettings, SegmentRequest, ...)
├─ routes/             # Request handlers grouped by topic (`clean`, `goto`)
├─ services/
│  ├─ client_connection.py  # Handles auth & MQTT sessions
│  └─ local_client.py       # Thin wrapper around roborock local commands
└─ utils/
   └─ globals.py       # Singleton helpers shared across modules
 ```

## Additional Information

- The service communicates with Roborock devices only after a successful cloud authentication.
- Make sure the vacuum cleaner and the host running this API share the same local network.
- The API is designed for internal/home‑automation use; do not expose it directly to the public Internet without proper
  authentication and rate‑limiting.
