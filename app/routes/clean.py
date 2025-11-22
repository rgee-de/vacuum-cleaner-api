import logging

from fastapi import APIRouter, HTTPException
from roborock import RoborockCommand

from app.model.cleaning_settings import CleaningSettings
from app.model.segment_request import SegmentRequest
from app.utils import globals

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/settings")
async def set_cleaning_settings(cleaning_settings: CleaningSettings):
    try:
        await globals.cc.local_client.set_clean_mode_s7maxv(
            fan_speed=cleaning_settings.fan_power,
            mop_mode=cleaning_settings.mop_mode,
            mop_intensity=cleaning_settings.water_box_mode
        )
        logger.info("Set cleaning settings: %s", cleaning_settings)
    except Exception as e:
        logger.error("Failed to set cleaning settings: %s", e)
        raise HTTPException(status_code=500, detail="Failed to set cleaning settings")


@router.post("/segments")
async def start_cleaning(request: SegmentRequest):
    try:
        await globals.cc.local_client.send_command_custom(RoborockCommand.APP_SEGMENT_CLEAN, params=[
            {"segments": request.segment_ids, "repeat": request.repeat}])
        logger.info("Start cleaning: %s", request)
    except Exception as e:
        logger.error("Failed to start cleaning: %s", e)
        raise HTTPException(status_code=500, detail="Failed to start cleaning")
