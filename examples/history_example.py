"""
This example shows how to get the event history from the mev-share API.
"""
import asyncio
from mev_share_py.client import MevShareClient

if __name__ == "__main__":
    STREAM_URL = "https://mev-share-goerli.flashbots.net/"
    client = MevShareClient.from_config('goerli', '../config.json')
    his_info = asyncio.run(client.get_event_history_info())

    params = {"blockStart": his_info['maxBlock'] - 1, "blockEnd": his_info['maxBlock']}
    his = asyncio.run(client.get_event_history(params=params))
