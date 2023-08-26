from mev_share_py.event_stream import SSEClient
import json
import datetime as dt
import time
import asyncio


if __name__ == "__main__":
    async def handle_event(event_data):
        data = json.loads(event_data.data)
        print("Received Event:", data['hash'][:5], dt.datetime.now())
        time.sleep(.1)


    stream_url = "https://mev-share.flashbots.net/"
    sse_client = SSEClient(stream_url)
    res = asyncio.run(sse_client.listen_for_events(handle_event), )