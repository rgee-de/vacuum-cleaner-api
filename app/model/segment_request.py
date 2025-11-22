from pydantic import BaseModel


class SegmentRequest(BaseModel):
    segment_ids: list[int]
    repeat: int = 1
