import aiohttp
from aiohttp_sse_client.client import EventSource
import asyncio
import json


class SSEClient:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        # self.queue = asyncio.

    async def _get_events(self):
        async with EventSource(self.stream_url, reconnection_time=10) as event_source:
            async for event in event_source:
                yield event

    async def listen_for_events(self, event_callback):
        async for event_data in self._get_events():
            await event_callback(event_data)
            # self.queu
            # asyncio.create_task(event_callback(event_data))


if __name__ == "__main__":
    async def handle_event(event_data):
        data = json.loads(event_data.data)
        print("Received Event:", data['hash'])


    stream_url = "https://mev-share.flashbots.net/"
    sse_client = SSEClient(stream_url)
    res = asyncio.run(sse_client.listen_for_events(handle_event), )
