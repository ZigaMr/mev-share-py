"""
This example shows how to get the event history from the mev-share API.
"""
import asyncio
from mev_share_py.event_stream import SSEClient


if __name__ == "__main__":
    # STREAM_URL = "https://mev-share.flashbots.net/"
    STREAM_URL = "https://mev-share-goerli.flashbots.net/"
    sse_client = SSEClient(STREAM_URL)
    his_info = asyncio.run(sse_client.get_event_history_info())

    params = {"blockStart": his_info['maxBlock']-100, "blockEnd": his_info['maxBlock'] }
    his = asyncio.run(sse_client.get_event_history(params=params))
