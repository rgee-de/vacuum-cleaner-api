import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from roborock import DeviceProp
from app.utils.globals import roborock_info
from app.config import LOG_LEVEL
from app.routes import goto, clean

# Configure logging for FastAPI
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def execute_action(action: str, func, *args):
    """Helper function to execute Roborock actions with standardized error handling."""
    try:
        result = await func(*args)
        return {"status": "success", "message": f"{action} successfully", "data": result}
    except Exception as e:
        logger.error("Error in %s: %s", action, e)
        raise HTTPException(status_code=500, detail=f"Failed to {action.lower()}")

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

app = FastAPI(lifespan=lifespan)
app.include_router(goto.router, prefix="/goto")
app.include_router(clean.router, prefix="/clean")

@app.get("/rooms")
async def rooms():
    """Fetch and return rooms JSON."""
    return await execute_action("retrieve rooms", roborock_info.get_rooms)

@app.get("/prop")
async def prop() -> dict:
    """Fetch and return device properties."""
    return await execute_action("retrieve device properties", roborock_info.get_device_prop)
