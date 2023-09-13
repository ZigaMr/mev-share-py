from dataclasses import dataclass
from typing import Optional, List, TypedDict


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


@dataclass
class PendingTransaction:
    """
    Data class for pending transactions.
    """
    hash: Optional[str] = None
    logs: Optional[List] = None
    to: Optional[str] = None
    function_selector: Optional[str] = None
    call_data: Optional[str] = None
    mev_gas_price: Optional[int] = None
    gas_used: Optional[int] = None


@dataclass
class PendingBundle:
    """
    Data class for pending bundles.
    """
    hash: Optional[str] = None
    logs: Optional[List] = None
    txs: Optional[List] = None
    mev_gas_price: Optional[int] = None
    gas_used: Optional[int] = None

