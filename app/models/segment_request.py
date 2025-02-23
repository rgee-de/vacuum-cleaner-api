from typing import List

from pydantic import BaseModel


class SegmentRequest(BaseModel):
    """Request model for specifying room segments and repeat count."""
    segment_ids: List[int]
    repeat: int = 1
