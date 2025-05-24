from typing import List, Dict

from pydantic import BaseModel


class CleaningModeSettings(BaseModel):
    """
    Represents valid ranges for fan power, water box mode, and mop mode
    for a particular cleaning mode.
    """
    fan_power: List[int]
    water_box_mode: List[int]
    mop_mode: List[int]


CLEANING_MODES: Dict[str, CleaningModeSettings] = {
    "Vac": CleaningModeSettings(
        fan_power=[101, 102, 103, 104, 108],
        water_box_mode=[200],
        mop_mode=[300, 304]
    ),
    "Mop": CleaningModeSettings(
        fan_power=[105],
        water_box_mode=[201, 202, 203],
        mop_mode=[304, 300, 301, 303]
    ),
    "Vac&Mop": CleaningModeSettings(
        fan_power=[101, 102, 103, 104],
        water_box_mode=[201, 202, 203],
        mop_mode=[304, 300]
    ),
    "Custom": CleaningModeSettings(
        fan_power=[106],
        water_box_mode=[204],
        mop_mode=[302]
    )
}

# fan_power:
# - 101: Quiet
# - 102: Balanced
# - 103: Turbo
# - 104: Max
# - 105: Off
# - 106: Custom
# - 108: Max+

# water_box_mode:
# - 200: Off
# - 201: Mild
# - 202: Moderate
# - 203: Intense
# - 204: Custom

# mop_mode:
# - 300: Standard
# - 301: Deep
# - 302: Custom
# - 303: Deep+
# - 304: Fast
