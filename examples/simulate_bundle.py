import asyncio
import json
import traceback

import requests
from web3 import Web3
from websockets import connect
from client_rpc import RPCClient
from web3 import Web3
from eth_account import Account
from api.types import BundleParams, TransactionOptions
from api.events import EventHistoryParams, PendingTransaction, PendingBundle
import datetime as dt
from client import MevShareClient

config = json.load(open('../mev_share_py/config.json'))

infura_ws_url = "wss://goerli.infura.io/ws/v3/{}".format(config['infura_key'])
infura_http_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])
web3 = Web3(Web3.HTTPProvider(infura_http_url))

async def handle_event(event_data: PendingTransaction) -> None:
    """
    Custom function to be called for each event.
    :param event_data: Message Event from the event stream.
    :return: None
    """
    print("Received Event:", event_data, dt.datetime.now())


def new_tx():
    # Replace these values with your actual ones
    private_key = "0xd937cd6f2c70c7dddac33419c75f344f31cf47267034801f9021045360e19535"
    to_address = "0xA59b230b8f43C888F554F6b9207462fb8b9B2dE7"

    # Connect to Ethereum provider
    w3 = Web3(Web3.HTTPProvider(infura_http_url))

    # Create an account from the private key
    account = Account.from_key(private_key)

    # Get the nonce
    nonce = w3.eth.get_transaction_count(account.address)

    # Define transaction parameters
    tip = 0  # Replace with your actual tip value
    flair = "im shariiiiiiing"  # Replace with your actual data

    transaction = {
        'type': 2,
        'chainId': w3.eth.chain_id,
        'to': to_address,
        'nonce': nonce,
        'value': 0,
        'gas': 22000,
        'data': Web3.to_hex(Web3.to_bytes(text=flair)),
        'maxFeePerGas': w3.to_wei(42, 'gwei') + tip,
        'maxPriorityFeePerGas': w3.to_wei(50, 'gwei') + tip,
    }

    # Sign the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the signed transaction
    # tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # print(f"Transaction Hash: {tx_hash.hex()}")
    return signed_transaction


async def get_event():
    async with connect(infura_ws_url) as ws:
        await ws.send('{"jsonrpc": "2.0", "id": 5, "method": "eth_subscribe", "params": ["newPendingTransactions"]}')
        subscription_response = await ws.recv()
        print(subscription_response)
        client = MevShareClient(api_url=config['relay_url_mainnet'],
                                stream_url=config['sse_url_mainnet'],
                                sign_key=config['sign_key'])

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                txHash = response['params']['result']
                print(txHash)
                # tx = web3.eth.get_transaction(txHash)
                tx2 = new_tx()
                params = {
                    'inclusion': {
                        'block': web3.eth.block_number + 1,
                        'max_block': web3.eth.block_number + 10,
                    },
                    'body': [{'hash': txHash, 'canRevert': True},
                             {'tx': tx2.rawTransaction.hex(), 'canRevert': True}],
                    'privacy': {
                        'hints': {
                            'tx_hash': True,
                            'calldata': True,
                            'logs': True,
                            'function_selector': True,
                        },
                        # 'builders': ['flashbots']
                    }
                }
                sim_options = {
                    'parent_block': web3.eth.block_number,
                }
                params = BundleParams(**params)
                return await client.simulate_bundle(params, sim_options)
            except Exception as e:
                traceback.print_exc()
                print(e)
            # return tx


if __name__ == "__main__":
    # STREAM_URL = "https://mev-share.flashbots.net/"
    # # STREAM_URL = "https://mev-share-goerli.flashbots.net/" # Goerli
    # SSE_CLIENT = SSEClient(STREAM_URL)
    # res = asyncio.run(
    # SSE_CLIENT.listen_for_events('transaction', handle_event),
    # )
    res = asyncio.run(get_event())