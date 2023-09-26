import json
from typing import Callable
import asyncio
import sys
from aiohttp_sse_client.client import MessageEvent

from mev_share_py.client_rpc import RPCClient
from mev_share_py.event_stream import SSEClient


class MevShareClient(RPCClient, SSEClient):
    """
    Wrapper class for interacting with the MEV-Share API and event stream.
    """
    def __init__(self,
                 api_url: str = None,
                 stream_url: str = None,
                 sign_key: str = None,
                 node_url: str = None,
                 ) -> None:

        if sign_key is None:
            raise KeyError("Either provide correct config.json url or custom sign_key parameter.")

        if node_url is None:
            raise KeyError("Either provide correct config.json url or custom node_url parameter.")

        if api_url is None:
            raise KeyError("Either provide correct config.json url or custom api_url parameter.")

        if stream_url is None:
            raise KeyError("Either provide correct config.json url or custom stream_url parameter.")

        # Multiple inheritance
        # When updating parent classes make sure not to use ambiguous keyword arguments
        super().__init__(api_url=api_url,
                         sign_key=sign_key,
                         node_url=node_url,
                         stream_url=stream_url)

    @classmethod
    def from_config(cls,
                    network: str = 'goerli',
                    config_dir: str = 'config.json'):
        """
        Class method for initializing the MevShareClient from a config file.
        :param network: goerli or mainnet (for now)
        :param config_dir: config.json file path
        :return: MevShareClient
        """
        with open(config_dir, encoding='utf-8') as json_file:
            config = json.load(json_file)
        cls.config = config
        return cls(sign_key=config['sign_key'],
                   node_url=config[network]['infura_url'].format(config['infura_key']),
                   api_url=config[network]['relay_url'],
                   stream_url=config[network]['sse_url'])

    async def listen_for_events(self,
                                event_type: str,
                                event_callback: Callable[[MessageEvent], None]) -> None:
        """
        :param event_type: Type of event to listen for. Valid values are "transaction" and "bundle".
        :param event_callback: The callback function to be called when an event is received.
        :return: None
        """
        # If running on Windows, set the event loop policy to WindowsSelectorEventLoopPolicy
        if "win" in sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        await super().listen_for_events(event_type, event_callback)
