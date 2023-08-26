
from web3 import Web3
import requests
import json
import datetime as dt
import time

# rpc_url = "https://ethereum-goerli.publicnode.com"
sse_url = "https://mev-share.flashbots.net/"
# relay_url = "https://relay-goerli.flashbots.net/"

# w3 = Web3(Web3.HTTPProvider(rpc_url))

def event_stream(url):
    with requests.get(url, stream=True) as response:
        for line in response.iter_lines():
            if line:  # filter out keep-alive new lines
                yield line


for events in event_stream(sse_url):
    try:
        data = json.loads(events[5:])
        print(data['hash'][:5], dt.datetime.now())
        time.sleep(.1)
    except:
        continue
    # print("==================")


