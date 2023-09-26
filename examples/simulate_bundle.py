import asyncio
from mev_share_py.api.types import BundleParams
from mev_share_py.client import MevShareClient
from send_bundle import new_tx




async def sim_private_tx_backrun():
    """
    Generate a bundle with two private transactions and simulate it.
    The "to" address and "private_key" are read from the config.json file.
    :return:
    """
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    tx1 = new_tx(client.w3, 0, client.config['private_key'], client.config['to'])
    tx2 = new_tx(client.w3, 1, client.config['private_key'], client.config['to'])
    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 10
        },
        'body': [{'tx': tx1.rawTransaction.hex(), 'canRevert': True},
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
        'parent_block': block_number,
    }
    params = BundleParams(**params)
    return await client.simulate_bundle(params, sim_options)

if __name__ == "__main__":
    res = asyncio.run(sim_private_tx_backrun())
    print(res)
