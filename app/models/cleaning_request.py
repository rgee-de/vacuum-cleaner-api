from typing import List

from pydantic import BaseModel

from app.models.cleaning_mode_settings import CLEANING_MODES


class CleaningRequest(BaseModel):
    mode: str
    fan_power: int
    water_box_mode: int
    mop_mode: int
    segment_ids: List[int]
    repeat: int = 1

    @classmethod
    def validate_settings(cls, mode: str, fan_power: int, water_box_mode: int, mop_mode: int):
        """Validate the selected settings against the mode's allowed values."""
        if mode not in CLEANING_MODES:
            raise ValueError("Invalid cleaning mode selected.")

        mode_settings = CLEANING_MODES[mode]
        if fan_power not in mode_settings.fan_power:
            raise ValueError(f"Invalid fan_power {fan_power} for mode {mode}")
        if water_box_mode not in mode_settings.water_box_mode:
            raise ValueError(f"Invalid water_box_mode {water_box_mode} for mode {mode}")
        if mop_mode not in mode_settings.mop_mode:
            raise ValueError(f"Invalid mop_mode {mop_mode} for mode {mode}")

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_settings(self.mode, self.fan_power, self.water_box_mode, self.mop_mode)
