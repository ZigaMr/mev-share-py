import asyncio
from web3 import Web3
from mev_share_py.client import MevShareClient


def new_tx(w3,
           nonce_add=0,
           private_key='0x',
           to_address='0x', ):
    """
    Creates a new transaction with the given parameters.
    :param w3: Web3 instance
    :param nonce_add: Nonce offset
    :param private_key: Private key
    :param to_address: To address
    :return: Signed transaction
    """
    account = w3.eth.account.from_key(private_key)
    # Get the nonce
    nonce = w3.eth.get_transaction_count(account.address) + nonce_add

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
        'maxPriorityFeePerGas': w3.to_wei(2, 'gwei') + tip,
    }

    # Sign the transaction
    signed_transaction = \
        w3.eth.account.sign_transaction(transaction, private_key)
    return signed_transaction


async def loop_tx():
    """
    Send out a private transaction every 5 minutes to the relay.
    Set the wallet and node settings in config.json
    :return:
    """
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    while True:
        # pylint: disable=redefined-outer-name
        tx = new_tx(client.w3, 0, client.config['private_key'], client.config['to'])
        print(tx)
        print(await client.send_transaction(
            tx.rawTransaction.hex(),
            {
                'max_block_number': await client.w3_async.eth.block_number + 10,
                'hints': {
                    'calldata': True,
                    'contract_address': True,
                    'function_selector': True,
                    'logs': True
                }
            }
        ))
        await asyncio.sleep(300)


if __name__ == "__main__":
    tx = asyncio.run(loop_tx())
    print(tx)
