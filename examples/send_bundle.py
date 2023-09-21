import asyncio
import json

from mev_share_py.client import MevShareClient
from web3 import Web3
from eth_account import Account
from api.types import BundleParams, TransactionOptions
from api.events import EventHistoryParams, PendingTransaction, PendingBundle


config = json.load(open('../mev_share_py/config.json'))

infura_ws_url = "wss://goerli.infura.io/ws/v3/{}".format(config['infura_key'])
infura_http_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])
web3 = Web3(Web3.HTTPProvider(infura_http_url))


def new_tx():
    # Replace these values with your actual ones
    private_key = config['private_key']
    to_address = config['to']

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

    return signed_transaction

async def build_and_send(tx1: PendingTransaction):
    tx2 = new_tx()  # Add raw tx here
    params = {
        'inclusion': {
            'block': web3.eth.block_number+1,
            # 'max_block': web3.eth.block_number+10,
        },
        'body': [{'hash': tx1.hash},
                 {'tx': tx2}],
        # 'privacy': {
        #     'hints': {
        #         'tx_hash': True,
        #         'calldata': True,
        #         'logs': True,
        #         'function_selector': True,
        #     },
        #     # 'builders': ['flashbots']
        # }
    }
    params = BundleParams(**params)
    return await client.send_bundle(params)



if __name__ == "__main__":
    client = MevShareClient()
    res = asyncio.run(
        client.listen_for_events('transaction', build_and_send)
    )