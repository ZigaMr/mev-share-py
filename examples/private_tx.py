import asyncio
import json
import requests
from web3 import Web3
from websockets import connect
from client_rpc import RPCClient


#  Mainnet
# relay_url = "https://api.mev-share.com/api/v1/"
# SSE_URL = "https://mev-share.flashbots.net/"

# Goerli
# sse_url = "https://mev-share-goerli.flashbots.net/"
relay_url = "https://relay-goerli.flashbots.net/"

config = json.load(open('../mev_share_py/config.json'))

infura_ws_url = "wss://goerli.infura.io/ws/v3/{}".format(config['infura_key'])
infura_http_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])
web3 = Web3(Web3.HTTPProvider(infura_http_url))

async def get_event():
    async with connect(infura_ws_url) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
        subscription_response = await ws.recv()
        print(subscription_response)
        client = RPCClient(relay_url=relay_url, private_key=config['private_key'])

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                txHash = response['params']['result']
                print(txHash)
                tx = web3.eth.get_transaction(txHash)
                client.send_transaction(tx.rawTransaction,
                                        {'max_block_number': web3.eth.block_number + 10})
            except Exception as e:
                print(e)
            return tx

if __name__ == "__main__":
    tx = asyncio.run(get_event())
