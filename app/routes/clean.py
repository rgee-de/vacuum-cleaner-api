import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.globals import roborock_info

logger = logging.getLogger(__name__)

router = APIRouter()

class SegmentRequest(BaseModel):
    segment_ids: list[int]

async def execute_cleaning(action: str, func, *args):
    """Helper function to execute Roborock cleaning commands with error handling."""
    try:
        await func(*args)
        return {"status": "success", "message": f"{action} successfully", "segments": args[0] if args else None}
    except Exception as e:
        logger.error("Error in %s: %s", action, e)
        raise HTTPException(status_code=500, detail=f"Failed to {action.lower()}")

@router.post("/custom")
async def clean_rooms_custom(request: SegmentRequest):
    """Starts cleaning for specific segment IDs."""
    await roborock_info.set_clean_mode_s7maxv()
    return await execute_cleaning("Cleaning started for segments", roborock_info.clean_room, request.segment_ids)
