import aiohttp

# TODO: Migrate from aiohttp_sse_client to aiohttp-sse
from aiohttp_sse_client.client import EventSource, MessageEvent
from aiohttp import ClientSession
import asyncio
import json, urllib.parse
import requests
from typing import Optional, List, Dict, Any, Callable
from data_types import EventHistoryParams


class SSEClient:

    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.reconnection_time = 5
        # self.queue = asyncio.

    async def __get_historical_data(self, url_suffix: str) -> Any:
        # TODO: Add error handling
        url = urllib.parse.urljoin(self.stream_url, "api/v1/")
        url = urllib.parse.urljoin(url, url_suffix)
        data = requests.get(url, timeout=10).json()
        return data

    async def _get_events(self) -> MessageEvent:
        session_timeout = aiohttp.ClientTimeout(
            total=None
        )  # Prevents aiohttp default timeout (300 seconds)
        async with EventSource(
                self.stream_url,
                reconnection_time=self.reconnection_time,
                session=ClientSession(timeout=session_timeout),
        ) as event_source:
            async for event in event_source:
                yield event

    async def listen_for_events(self, event_callback: Callable[[str], None]) -> None:
        async for event_data in self._get_events():
            # await event_callback(event_data)
            # self.queu
            try:
                asyncio.create_task(event_callback(event_data))
            except asyncio.TimeoutError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                continue

    async def get_event_history_info(self) -> List:
        return await self.__get_historical_data("history/info")

    async def get_event_history(self, params: Dict = None) -> List:
        # TODO: set params to dataclass type for static analysis
        _params = params or {}
        query = "&".join([f"{key}={value}" for key, value in _params.items()])

        res: List = await self.__get_historical_data("history" + f"?{query}")
        # return [EventHistoryEntry(entry) for entry in res]
        return res


if __name__ == "__main__":
    pass
