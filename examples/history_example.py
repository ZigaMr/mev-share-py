"""
This example shows how to get the event history from the mev-share API.
"""
import asyncio
from mev_share_py.event_stream import SSEClient


if __name__ == "__main__":
    STREAM_URL = "https://mev-share.flashbots.net/"
    sse_client = SSEClient(STREAM_URL)
    res = asyncio.run(sse_client.get_event_history_info())

    params = {"blockStart": 17999052, "blockEnd": 17999152}
    res = asyncio.run(sse_client.get_event_history(params=params))
