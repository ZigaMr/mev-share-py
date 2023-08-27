"""
Async event stream example,
prints out the first 5 characters of the block hash for each event.
"""

import json
import datetime as dt
import asyncio
from aiohttp_sse_client.client import MessageEvent
from mev_share_py.event_stream import SSEClient


if __name__ == "__main__":
    async def handle_event(event_data: MessageEvent) -> None:
        """
        Custom function to be called for each event.
        :param event_data: Message Event from the event stream.
        :return: None
        """
        data = json.loads(event_data.data)
        print("Received Event:", data['hash'][:5], dt.datetime.now())


    STREAM_URL = "https://mev-share.flashbots.net/"
    SSE_CLIENT = SSEClient(STREAM_URL)
    res = asyncio.run(SSE_CLIENT.listen_for_events(handle_event), )