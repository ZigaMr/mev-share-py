import asyncio
import os
from mev_share_py.api.types import BundleParams
from mev_share_py.client import MevShareClient
from mev_share_py.api.events import PendingTransaction
from send_bundle import new_tx

# Set environment variables before running this script
try:
    private_key = os.environ.get('PRIVATE_KEY')
    to = os.environ.get('TO_ADDRESS')
    api_url = os.environ.get('API_URL')
    stream_url = os.environ.get('STREAM_URL')
    sign_key = os.environ.get('SIGN_KEY')
    node_url = os.environ.get('NODE_URL')
except KeyError as e:
    print(f"Please set the environment variable {e}")
    exit(1)



async def sim_private_tx_backrun(tx: PendingTransaction, client: MevShareClient):
    """
    Build a bundle containing private tx hash from event stream and custom signed tx.
    Send the bundle to the relay and simulate it.
    :return: None
    """

    backrun_transaction = new_tx(client.w3, 0, private_key, to)  # Add raw tx here
    backrun_signed_tx = backrun_transaction.rawTransaction.hex()
    pending_tx = tx.hash

    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 30
        },
        'body': [
            {'hash': pending_tx},
            {'tx': backrun_signed_tx, 'can_revert': False},
            ],
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
    await client.send_bundle(params) # Send bundle to the relay so the tx lands onchain
    return await client.simulate_bundle(params, sim_options)

if __name__ == "__main__":
    client = MevShareClient(api_url=api_url, #  "https://relay-goerli.flashbots.net/",
                            stream_url=stream_url,  #  "https://mev-share-goerli.flashbots.net/",
                            sign_key=sign_key,  #  Private key to sign the bundle
                            node_url=node_url #  Geth node url
                            )
    res = asyncio.run(
        client.listen_for_events('transaction', sim_private_tx_backrun),
    )
