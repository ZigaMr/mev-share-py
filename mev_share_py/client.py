"""
Client library for interacting with the MEV-Share API and event stream.
"""
from typing import Callable
import asyncio
import sys
import warnings

from aiohttp_sse_client.client import MessageEvent
from mev_share_py.client_rpc import RPCClient
from mev_share_py.event_stream import SSEClient


class MevShareClient(RPCClient, SSEClient):
    """
    Wrapper class for interacting with the MEV-Share API and event stream.
    """
    def __init__(self,
                 rpc_url: str = None,
                 stream_url: str = None,
                 sign_key: str = None,
                 node_url: str = None,
                 ) -> None:

        if sign_key is None:
            warnings.warn("No sign_key parameter provided.")

        if node_url is None:
            warnings.warn("No node_url parameter provided.")

        if rpc_url is None:
            warnings.warn("No rpc_url parameter provided.")

        if stream_url is None:
            warnings.warn("No stream_url parameter provided.")

        # Multiple inheritance
        super().__init__(rpc_url=rpc_url,
                         sign_key=sign_key,
                         node_url=node_url,
                         stream_url=stream_url)

    async def listen_for_events(self,
                                event_type: str,
                                event_callback: Callable[[MessageEvent], None]) -> None:
        """
        :param event_type: Type of event to listen for. Valid values are "transaction" and "bundle".
        :param event_callback: The callback function to be called when an event is received.
        :return: None
        """
        # If running on Windows, set the event loop policy to WindowsSelectorEventLoopPolicy
        if "win" in sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        await super().listen_for_events(event_type, event_callback)
