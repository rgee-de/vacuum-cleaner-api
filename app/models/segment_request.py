from typing import List
from pydantic import BaseModel


class SegmentRequest(BaseModel):
    """
    Represents a request for specifying room segments and repeat count
    for cleaning operations.
    """
    segment_ids: List[int]
    repeat: int = 1
