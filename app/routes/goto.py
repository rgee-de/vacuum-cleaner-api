import logging
from fastapi import APIRouter, HTTPException

from app.config import CLEANING_X, CLEANING_Y
from app.utils.globals import roborock_info

logger = logging.getLogger(__name__)
router = APIRouter()


async def execute_command(action: str, func, *args):
    """
    Helper function to execute Roborock commands with standardized error handling.
    """
    try:
        await func(*args)
        return {"status": "success", "message": f"Device {action} successfully"}
    except Exception as e:
        logger.error("Error during '%s': %s", action, e)
        raise HTTPException(status_code=500, detail=f"Failed to {action}")


@router.post("/cleaning")
async def go_to_coordinates():
    """
    Direct the vacuum to predefined cleaning coordinates (e.g., a custom location).
    """
    return await execute_command("sent to cleaning location", roborock_info.go_to, CLEANING_X, CLEANING_Y)


@router.post("/{x}/{y}")
async def go_to_coordinates(x: int, y: int):
    """
    Direct the vacuum to the specified (x, y) coordinates.
    """
    return await execute_command(f"sent to coordinates ({x}, {y})", roborock_info.go_to, x, y)


@router.post("/charging")
async def go_to_charging():
    """
    Send the vacuum back to its charging station.
    """
    return await execute_command("sent to charging station", roborock_info.charge)
