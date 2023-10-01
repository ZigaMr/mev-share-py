# pylint: disable=missing-module-docstring
import asyncio
from examples.private_tx import new_tx
from mev_share_py.client import MevShareClient
from mev_share_py.api.types import BundleParams
from mev_share_py.api.events import PendingTransaction



async def build_and_send(tx: PendingTransaction, client: MevShareClient):
    """
    Generate a bundle containing private tx hash and backrun signed tx.
    :return:
    """
    private_key = '<private_key>
    to = '<to_address>'
    backrun_transaction = new_tx(client.w3, 0, private_key, to)  # Add raw tx here

    user_tx_hash = tx.hash
    backrun_signed_tx = backrun_transaction.rawTransaction.hex()
    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 10,
        },
        'body': [
            {'hash': user_tx_hash},
            {'tx': backrun_signed_tx, 'can_revert': True},
        ],
        # 'privacy': {
        #     'hints': {
        #         'tx_hash': True,
        #         'calldata': True,
        #         'logs': True,
        #         'function_selector': True,
        #     },
            # 'builders': ['flashbots']
        # }
    }
    params = BundleParams(**params)
    print(await client.send_bundle(params))

if __name__ == "__main__":
    client = MevShareClient(api_url='<RPC_url>', #  "https://relay-goerli.flashbots.net/",
                            stream_url='<SSE_url>',  #  "https://mev-share-goerli.flashbots.net/",
                            sign_key='<sign_key>',  #  Private key to sign the bundle
                            node_url='<node_url>' #  Geth node url
                            )

    res = asyncio.run(
        client.listen_for_events('transaction', build_and_send),
    )