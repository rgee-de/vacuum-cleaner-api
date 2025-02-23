import asyncio
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.config import LOG_LEVEL, ORIGINS, WEBSOCKET_URL
from app.models.cleaning_mode_settings import CLEANING_MODES
from app.routes import goto, clean
from app.utils.globals import roborock_info, websocket_manager

# Configure logging for FastAPI
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def execute_action(action: str, func, *args):
    """
    Helper function to execute Roborock actions with standardized error handling.
    """
    try:
        result = await func(*args)
        return {
            "status": "success",
            "message": f"{action} successfully",
            "data": result
        }
    except Exception as e:
        logger.error("Error during '%s': %s", action, e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {action.lower()}"
        )


async def broadcast_device_props():
    """
    Continuously broadcast device properties every 5 seconds to all connected clients.
    """
    while True:
        if len(websocket_manager.active_connections) > 0:
            try:
                device_props = await roborock_info.get_device_prop()
                device_props_dict = asdict(device_props)

                # Convert datetime objects to strings
                device_props_json = json.dumps(device_props_dict, default=str)

                # Broadcast JSON data to all connected clients
                await websocket_manager.broadcast({
                    "status": "success",
                    "data": json.loads(device_props_json)
                })
                logger.info("Successfully retrieved device properties.")
            except Exception as e:
                logger.error("Error retrieving device properties: %s", e)
                await websocket_manager.broadcast({
                    "status": "error",
                    "message": str(e)
                })
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Handle startup and shutdown lifecycle events using an async context manager.
    """
    # Startup
    await roborock_info.initialize()
    logger.info("RoborockInfo initialized on startup.")
    asyncio.create_task(broadcast_device_props())

    yield  # Application runs after this point until shutdown

    # Shutdown
    await roborock_info.disconnect_mqtt()
    logger.info("RoborockInfo disconnected on shutdown.")


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(goto.router, prefix="/goto")
app.include_router(clean.router, prefix="/clean")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template directory
templates = Jinja2Templates(directory="app/templates")


@app.get("/rooms")
async def rooms():
    """
    Fetch and return the list of rooms.
    """
    return await execute_action("retrieve rooms", roborock_info.get_rooms)


@app.get("/prop")
async def prop() -> dict:
    """
    Fetch and return device properties.
    """
    return await execute_action("retrieve device properties", roborock_info.get_device_prop)


@app.post("/stop")
async def stop() -> dict:
    """
    Stop the current cleaning task.
    """
    return await execute_action("stop current task", roborock_info.stop)


@app.post("/pause")
async def pause() -> dict:
    """
    Pause the current cleaning task.
    """
    return await execute_action("pause current task", roborock_info.pause)


@app.get("/modes")
async def get_cleaning_modes():
    """
    Return valid fan_power, water_box_mode, and mop_mode for each cleaning mode.
    """
    return CLEANING_MODES


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        await websocket_manager.disconnect(websocket)


@app.get("/")
def get_websocket_example(request: Request):
    """
    Render a template demonstrating WebSocket usage.
    """
    return templates.TemplateResponse(
        "websocket_example.html",
        {"request": request, "websocket_url": WEBSOCKET_URL}
    )
