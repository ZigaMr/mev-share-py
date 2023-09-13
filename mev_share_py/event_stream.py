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
from api.events import EventHistoryParams, PendingTransaction, PendingBundle
from web3 import Web3, Account
import json


class SSEClient:
    """
    Client library for interacting with the MEV-Share event stream.
    """

    def __init__(self,
                 stream_url: str = "https://mev-share.flashbots.net/",
                 private_key: str = None):
        self.stream_url = stream_url
        self.reconnection_time = 5
        self.account = Account.from_key(private_key) if private_key else None
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

    async def _on_transaction(self,
                              event: Dict,
                              event_callback: Callable[[MessageEvent], None]) -> Any:
        """
        Filters for transaction type events.
        :param event: Message Event from the event stream.
        :param event_callback: Callback function to be called for each filtered event.
        :return: None
        """
        if not event['txs']:
            tx = {
                "hash": event['hash'],
                "logs": event['logs'] if 'logs' in event else None,
                "to": None,
                "function_selector": None,
                "call_data": None,
                "mev_gas_price": None,
                "gas_used": None,
            }
        elif len(event['txs']) == 1:
            tx = {
                "hash": event['hash'],
                "logs": event['logs'] if 'logs' in event else None,
                "to": event['txs'][0]['to'] if 'to' in event['txs'][0] else None,
                "function_selector": event['txs'][0]['functionSelector'] if 'functionSelector' in event['txs'][0] else None,
                "call_data": event['txs'][0]['callData'] if 'callData' in event['txs'][0] else None,
                "mev_gas_price": event['txs'][0]['mevGasPrice'] if 'mevGasPrice' in event['txs'][0] else None,
                "gas_used": event['txs'][0]['gasUsed'] if 'gasUsed' in event['txs'][0] else None,
            }
        else:
            return
        return await event_callback(PendingTransaction(**tx))

    async def _on_bundle(self,
                         event: Dict,
                         event_callback: Callable[[MessageEvent], None]) -> Any:
        """
        Filters for bundle type events.
        :param event: Message Event from the event stream.
        :param event_callback: Callback function to be called for each filtered event.
        :return: None
        """
        if event['txs'] and len(event['txs']) > 1:
            bundle = {
                "hash": event['hash'],
                "logs": event['logs'] if 'logs' in event else None,
                "txs": event['txs'],
                "mev_gas_price": event['mevGasPrice'] if 'mevGasPrice' in event else None,
                "gas_used": event['gasUsed'] if 'gasUsed' in event else None,
            }
            return await event_callback(PendingBundle(**bundle))

    async def listen_for_events(self,
                                event_type: str,
                                event_callback: Callable[[MessageEvent], None]) -> None:
        """
        Wrapper for _get_events that calls the event_callback function for each event.
        :param event_callback: Custom function to be called for each event.
        :return: None
        """

        if event_type == "transaction":
            event_handler = self._on_transaction
        elif event_type == "bundle":
            event_handler = self._on_bundle
        else:
            raise NotImplementedError("Invalid event type. Must be 'transaction' or 'bundle'.")

        async for event_data in self._get_events():
            print(event_data)
            try:
                asyncio.create_task(event_handler(json.loads(event_data.data), event_callback))
            except asyncio.TimeoutError:
                print('Timeout Error')
            except Exception as e:  # pylint: disable=broad-except
                print(e)

    async def get_event_history_info(self) -> Dict:
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
