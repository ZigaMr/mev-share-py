"""
Library for interacting with the MEV-Share event stream.
"""

import asyncio
from typing import List, Dict, Any, Callable
import urllib.parse
import requests
# TODO: Migrate from aiohttp_sse_client to aiohttp-sse
from aiohttp_sse_client.client import EventSource, MessageEvent
from aiohttp import ClientSession, ClientTimeout


class SSEClient:
    """
    Client library for interacting with the MEV-Share event stream.
    """

    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.reconnection_time = 5
        # self.queue = asyncio.

    async def __get_historical_data(self, url_suffix: str) -> Any:
        """
        Private method for getting historical data from the MEV-Share API.
        :param url_suffix: The url suffix to be appended to the base url.
        :return: Dictionary of historical data.
        """
        # TODO: Add error handling
        url = urllib.parse.urljoin(self.stream_url, "api/v1/")
        url = urllib.parse.urljoin(url, url_suffix)
        data = requests.get(url, timeout=10).json()
        return data

    async def _get_events(self) -> MessageEvent:
        """
        Async generator for getting events from the MEV-Share event stream.
        :return: Message Event from the event stream.
        """
        session_timeout = ClientTimeout(
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
        """
        Wrapper for _get_events that calls the event_callback function for each event.
        :param event_callback: Custom function to be called for each event.
        :return: None
        """
        async for event_data in self._get_events():
            try:
                asyncio.create_task(event_callback(event_data))
            except asyncio.TimeoutError as e:
                print(e)
                continue
            except Exception as e:  # pylint: disable=broad-except
                print(e)
                continue

    async def get_event_history_info(self) -> List:
        """
        Fetch event history parameters by making an HTTP GET request
        to the instance’s streamUrl at the /api/v1/history/info endpoint.
        :return: List of event history info.
        """
        return await self.__get_historical_data("history/info")

    async def get_event_history(self, params: Dict = None) -> List:
        """
        Fetch event history by making an HTTP GET request
        to the instance’s streamUrl at the /api/v1/history endpoint.
        :param params: Optional parameters to refine the query.
        :return:
        """
        # TODO: set params to dataclass type for static analysis
        _params = params or {}
        query = "&".join([f"{key}={value}" for key, value in _params.items()])

        res: List = await self.__get_historical_data("history" + f"?{query}")
        # return [EventHistoryEntry(entry) for entry in res]
        return res


if __name__ == "__main__":
    pass
