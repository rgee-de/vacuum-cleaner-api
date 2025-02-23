import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.cleaning_settings import CleaningSettings
from app.utils.globals import roborock_info

logger = logging.getLogger(__name__)

router = APIRouter()


class SegmentRequest(BaseModel):
    segment_ids: list[int]
    repeat: int = 1


async def execute_cleaning(action: str, func, *args):
    """Helper function to execute Roborock cleaning commands with error handling."""
    try:
        await func(*args)
        return {"status": "success", "message": f"{action} successfully", "segments": args[0] if args else None}
    except Exception as e:
        logger.error("Error in %s: %s", action, e)
        raise HTTPException(status_code=500, detail=f"Failed to {action.lower()}")

@router.post("/settings")
async def set_cleaning_settings(request: CleaningSettings):
    """Set cleaning settings for the robot without starting it."""
    try:
        await roborock_info.set_clean_mode_s7maxv(
            fan_speed=request.fan_power,
            mop_mode=request.mop_mode,
            mop_intensity=request.water_box_mode
        )
        return {"status": "success", "message": "Cleaning settings set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segments")
async def start_cleaning(request: SegmentRequest):
    """Start cleaning with the previously set settings."""
    try:
        return await execute_cleaning(
            "Cleaning started",
            roborock_info.clean_room,
            request.segment_ids,
            request.repeat
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
