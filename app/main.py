import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from roborock import RoborockCommand, DeviceProp

from app.config import ORIGINS, LOG_LEVEL, ROBOROCK_USER, ROBOROCK_PASSWORD
from app.model.cleaning_mode_settings import CLEANING_MODES, CleaningModeSettings
from app.model.room_summary import RoomSummary
from app.routes import goto, clean
from app.services.client_connection import ClientConnection
from app.utils import globals

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        logger.info("Initializing Roborock connection...")
        globals.cc = ClientConnection(ROBOROCK_USER, ROBOROCK_PASSWORD)
        await globals.cc.initialize()
        logger.info("Roborock connection initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize RoborockInfo: {e}")

    yield

    try:
        logger.info("Shutting down Roborock connection...")
        await globals.cc.local_client.async_disconnect()
        logger.info("RoborockInfo disconnected on shutdown.")
    except Exception as e:
        logger.error(f"Error during Roborock shutdown: {e}")


# Initialize FastAPI application
app = FastAPI(lifespan=lifespan)
app.include_router(goto.router, prefix="/goto")
app.include_router(clean.router, prefix="/clean")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/prop")
async def get_properties() -> DeviceProp:
    try:
        prop = await globals.cc.local_client.get_prop()
        logger.info("Get prop: %s", prop)
        return prop
    except Exception as e:
        logger.error("Failed to fetch prop: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch prop")


@app.get("/rooms")
async def get_rooms() -> list[RoomSummary]:
    try:
        rooms = await globals.cc.get_rooms()
        logger.info("Get rooms: %s", rooms)
        return rooms
    except Exception as e:
        logger.error("Failed to fetch rooms: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch rooms")


@app.get("/modes")
async def get_cleaning_modes() -> dict[str, CleaningModeSettings]:
    return CLEANING_MODES


@app.post("/stop")
async def stop():
    try:
        await globals.cc.local_client.send_command_custom(RoborockCommand.APP_STOP)
        logger.info("Send stop command")
    except Exception as e:
        logger.error("Failed to send stop command: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send stop command")


@app.post("/pause")
async def pause():
    try:
        await globals.cc.local_client.send_command_custom(RoborockCommand.APP_PAUSE)
        logger.info("Send pause command")
    except Exception as e:
        logger.error("Failed to send pause command: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send pause command")
