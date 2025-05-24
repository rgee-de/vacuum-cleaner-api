import logging

from fastapi import APIRouter, HTTPException
from roborock import RoborockCommand

from app.config import CLEANING_X, CLEANING_Y
from app.utils import globals

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/maintenance")
async def go_to_coordinates():
    x = CLEANING_X
    y = CLEANING_Y

    try:
        await globals.cc.local_client.send_command_custom(RoborockCommand.APP_GOTO_TARGET, params=[x, y])
        logger.info("Send goto command to position: x:%s y:%s", x, y)
    except Exception as e:
        logger.error("Failed to send goto command: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send goto command")


@router.post("/charge")
async def go_to_coordinates():
    try:
        await globals.cc.local_client.send_command_custom(RoborockCommand.APP_CHARGE, params=[])
        logger.info("Send goto charge command")
    except Exception as e:
        logger.error("Failed to send goto charge command: %s", e)
        raise HTTPException(status_code=500, detail="Failed to send goto charge command")
