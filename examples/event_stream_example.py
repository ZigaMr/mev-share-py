"""
Async event stream example,
prints out the first 5 characters of the block hash for each event.
"""

import datetime as dt
import asyncio
from mev_share_py.client import MevShareClient
from mev_share_py.api.events import PendingTransaction


async def handle_event(event_data: PendingTransaction) -> None:
    """
    Custom function to be called for each event.
    :param event_data: Message Event from the event stream.
    :return: None
    """
    print("Received Event:", event_data, dt.datetime.now())


if __name__ == "__main__":

    # STREAM_URL = "https://mev-share.flashbots.net/"
    STREAM_URL = "https://mev-share-goerli.flashbots.net/"  # Goerli
    client = MevShareClient.from_config('goerli', '../config.json')
    res = asyncio.run(
        client.listen_for_events('transaction', handle_event),
    )
