import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.utils.globals import roborock_info
from app.config import LOG_LEVEL

# Configure logging for FastAPI
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Handle startup and shutdown lifecycle events using lifespan."""
    try:
        await roborock_info.initialize()
        logger.info("RoborockInfo initialized successfully on startup")
        yield  # Control returns to the FastAPI application here
    except Exception as e:
        logger.error("Failed to initialize RoborockInfo on startup: %s", e)
    finally:
        await roborock_info.disconnect_mqtt()
        logger.info("RoborockInfo disconnected on shutdown")

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/room_mappings")
async def room_mappings():
    """Fetch and return room mappings as JSON."""
    try:
        mappings = await roborock_info.get_room_mappings()
        return {"room_mappings": mappings}
    except Exception as e:
        logger.error("Error in room_mappings endpoint: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve room mappings")



# To Cleaning Point
# Back to Station
# Clean Room(List with info)