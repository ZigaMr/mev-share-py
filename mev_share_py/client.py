from client_rpc import RPCClient
from event_stream import SSEClient
import json
from web3 import Web3
from web3.types import TxParams
from api.events import EventHistoryParams, PendingTransaction, PendingBundle
from api.types import TransactionOptions
from typing import Callable
import asyncio
import sys
from aiohttp_sse_client.client import MessageEvent


class MevShareClient(RPCClient, SSEClient):
    def __init__(self,
                 api_url: str = "https://relay-goerli.flashbots.net/",
                 stream_url: str = "https://mev-share-goerli.flashbots.net/",
                 sign_key: str = None,
                 node_url: str = None):

        if sign_key is None:
            config = json.load(open('../mev_share_py/config.json'))
            sign_key = config['sign_key']
        if node_url is None:
            config = json.load(open('../mev_share_py/config.json'))
            node_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])

        # Multiple inheritance
        # When updating parent classes make sure not to use ambiguous keyword arguments
        super().__init__(api_url=api_url,
                         sign_key=sign_key,
                         node_url=node_url,
                         stream_url=stream_url)

    async def listen_for_events(self,
                                event_type: str,
                                event_callback: Callable[[MessageEvent], None]) -> None:
        """
        :param event_type: The type of event to listen for. Valid values are "transaction" and "bundle".
        :param event_callback: The callback function to be called when an event is received.
        :return: None
        """
        # If running on Windows, set the event loop policy to WindowsSelectorEventLoopPolicy
        if "win" in sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        await super().listen_for_events(event_type, event_callback)
