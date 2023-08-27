"""
Synchronous Event Stream Example,
prints out the first 5 characters of the block hash for each event.
"""

import json
import datetime as dt
import traceback
import requests

# rpc_url = "https://ethereum-goerli.publicnode.com"
# relay_url = "https://relay-goerli.flashbots.net/"
# w3 = Web3(Web3.HTTPProvider(RPC_URL))
SSE_URL = "https://mev-share.flashbots.net/"


def event_stream(url: str) -> bytes:
    """
    Generator function for getting events from the MEV-Share event stream.
    :param url: The url of the event stream.
    :return:
    """
    with requests.get(url, stream=True, timeout=100) as response:
        for line in response.iter_lines():
            if line:  # filter out keep-alive new lines
                yield line

if __name__ == '__main__':
    for event in event_stream(SSE_URL):
        try:
            data = json.loads(event[5:])
            print(data['hash'][:5], dt.datetime.now())
        except: # pylint: disable=bare-except
            traceback.print_exc()
