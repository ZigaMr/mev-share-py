"""
This file contains data types used in the mev_share_py package.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EventHistoryParams:
    """
    Data class for event history parameters.
    """

    block_start: Optional[int] = None
    block_end: Optional[int] = None
    timestamp_start: Optional[int] = None
    timestamp_end: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
