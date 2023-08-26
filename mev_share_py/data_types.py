from dataclasses import dataclass
from typing import Optional

@dataclass
class EventHistoryParams:
    blockStart: Optional[int] = None
    blockEnd: Optional[int] = None
    timestampStart: Optional[int] = None
    timestampEnd: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
