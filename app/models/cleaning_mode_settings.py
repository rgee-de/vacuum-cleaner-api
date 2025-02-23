from typing import List, Dict

from pydantic import BaseModel


class CleaningModeSettings(BaseModel):
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
# - Leise / quiet: 101
# - Normal / balanced: 102
# - Turbo / turbo: 103
# - Max / max: 104
# - Aus / off: 105
# - Individuell / custom: 106
# - Max+ / max+: 108
#
# water_box_mode:
# - Aus / off: 200
# - Sanft / mild: 201
# - Standard / moderate: 202
# - Intensiv / intense: 203
# - Individuell / custom: 204
#
# mop_mode:
# - Standard / standard: 300
# - Gründlich / deep: 301
# - Individuell / custom: 302
# - Gründlich+ / deep_plus: 303
# - Schnell / fast: 304
