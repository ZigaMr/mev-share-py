import asyncio
import json
import requests
from web3 import Web3
from websockets import connect
from client_rpc import RPCClient
from web3 import Web3
from eth_account import Account



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
        'maxPriorityFeePerGas': w3.to_wei(20, 'gwei') + tip,
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
        client = RPCClient(api_url=config['relay_url_goerli'], private_key=config['sign_key'])

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
                response = json.loads(message)
                txHash = response['params']['result']
                print(txHash)
                # tx = web3.eth.get_transaction(txHash)
                tx = new_tx()
                return await client.send_transaction(tx.rawTransaction.hex(),
                                                     {'max_block_number': web3.eth.block_number + 1000,
                                                      'hints': {
                                                          'tx_hash': True,
                                                          'calldata': True,
                                                          'logs': True,
                                                          'function_selector': True,
                                                      },
                                                      }
                                                     )
            except Exception as e:
                print(e)
            # return tx


async def loop_tx():
    client = RPCClient(api_url=config['relay_url_goerli'],
                       sign_key=config['sign_key'])
    while True:
        tx = new_tx()
        print(tx)
        print(await client.send_transaction(tx.rawTransaction.hex(),
                                            {'max_block_number': web3.eth.block_number + 10,
                                             'hints': {
                                                 'calldata': True,
                                             }
                                             }
                                            ))
        await asyncio.sleep(60)


if __name__ == "__main__":
    tx = asyncio.run(loop_tx())
    print(tx)
