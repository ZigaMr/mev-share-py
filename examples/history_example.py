"""
This example shows how to get the event history from the mev-share API.
"""
import asyncio
from client import MevShareClient


if __name__ == "__main__":
    # STREAM_URL = "https://mev-share.flashbots.net/"
    STREAM_URL = "https://mev-share-goerli.flashbots.net/"
    # sse_client = SSEClient(STREAM_URL)
    client = MevShareClient(stream_url=STREAM_URL)
    his_info = asyncio.run(client.get_event_history_info())

    params = {"blockStart": his_info['maxBlock']-100, "blockEnd": his_info['maxBlock'] }
    his = asyncio.run(client.get_event_history(params=params))
