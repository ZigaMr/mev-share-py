# pylint: disable=missing-module-docstring
import asyncio
from examples.private_tx import new_tx
from mev_share_py.client import MevShareClient
from mev_share_py.api.types import BundleParams



async def build_and_send():
    """
    Generate a bundle with two private transactions and send it.
    :return:
    """
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    tx1 = new_tx(client.w3, 0, client.config['private_key'], client.config['to'])  # Add raw tx here
    tx2 = new_tx(client.w3, 1, client.config['private_key'], client.config['to'])  # Add raw tx here
    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 10,
        },
        'body': [
            {'tx': tx1.rawTransaction.hex()},
            {'tx': tx2.rawTransaction.hex()}],
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
    params = BundleParams(**params)
    print(await client.send_bundle(params))

if __name__ == "__main__":
    asyncio.run(build_and_send())
