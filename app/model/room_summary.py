from pydantic import BaseModel


class RoomSummary(BaseModel):
    name: str
    id: int
    segment_id: int
