from mev_share_py.event_stream import SSEClient
import json
import datetime as dt
import time
import asyncio
from data_types import EventHistoryParams

if __name__ == "__main__":
    stream_url = "https://mev-share.flashbots.net/"
    sse_client = SSEClient(stream_url)
    res = asyncio.run(sse_client.get_event_history_info())

    params = {
        'blockStart': 17999052,
        'blockEnd': 17999152
    }
    res = asyncio.run(sse_client.get_event_history(params=params))
