"""
Client for interacting with the mev-share JSON-RPC API
"""
import json
from rlp import encode
from eth_utils import to_bytes
import requests

from web3 import Web3, Account, eth
from web3.datastructures import AttributeDict
from mev_share_py.flashbots_signature import get_rpc_request
from mev_share_py.api.types \
    import TransactionOptions, BundleParams, SimBundleOptions
from mev_share_py.api.mungers \
    import munge_private_tx_params, munge_bundle_params, munge_sim_bundle_options


class RPCClient:
    """
    Parent class for interacting with the mev-share JSON-RPC API
    """

    def __init__(self,
                 rpc_url: str,
                 sign_key: str = None,
                 node_url: str = None,
                 **kwargs):
        self.rpc_url = rpc_url
        self.account = Account.from_key(sign_key) if sign_key else None  # pylint: disable=no-value-for-parameter
        self.w3 = Web3(Web3.HTTPProvider(node_url)) if node_url else None
        self.w3_async = Web3(
            Web3.AsyncHTTPProvider(node_url),
            modules={'eth': (eth.AsyncEth,)}, middlewares=[]
        )
        super().__init__(**kwargs)

    async def __handle_request(self,
                               params,
                               method):
        headers, _, body = await get_rpc_request(params,
                                                 method,
                                                 self.account,
                                                 "1")
        print(body)
        return requests.post(url=self.rpc_url,
                             data=json.dumps(body),
                             headers=headers,
                             timeout=300).json()

    def _rlp_encode(self, tx: AttributeDict):
        """
        RLP encodes a transaction since get_raw_transaction() is not available on most public nodes.
        :param tx: Transaction object
        :return: RLP encoded signed transaction (hex string)
        """

        to_as_bytes = to_bytes(hexstr=tx["to"])
        # Legacy
        if tx['type'] == 0:
            encoded_tx = '0x' + encode(
                [tx['nonce'], tx['gasPrice'], tx['gas'], to_as_bytes,
                 tx['value'], tx['input'], tx['v'], tx['r'], tx['s']]).hex()
        # AccessList
        elif tx['type'] == 1:
            encoded_tx = '0x01' + encode(
                [tx['chainId'], tx['nonce'], tx['gasPrice'], tx['gas'], to_as_bytes, tx['value'],
                 tx['input'], tx['accessList'], tx['v'], tx['r'], tx['s']]).hex()
        # EIP-1559
        elif tx['type'] == 2:
            encoded_tx = "0x02" + encode(
                [tx['chainId'], tx['nonce'], tx['maxPriorityFeePerGas'],
                 tx['maxFeePerGas'], tx['gas'], to_as_bytes, tx['value'],
                 tx['input'], tx['accessList'], tx['v'], tx['r'], tx['s']]).hex()
        return encoded_tx

    async def send_transaction(self,
                               signed_tx: str,
                               options: TransactionOptions) -> str:
        """

        :param signed_tx: Signed transaction (hex string)
        :param options: Transaction options
        :return: Transaction hash
        """
        munger_params = munge_private_tx_params(signed_tx, options)
        return await self.__handle_request(munger_params, "eth_sendPrivateTransaction")

    async def send_bundle(self, params: BundleParams) -> str:
        """
        
        :param params:  Bundle parameters
        :return:  Transaction hash
        """
        munger_params = munge_bundle_params(params)
        return await self.__handle_request(munger_params, "mev_sendBundle")

    async def simulate_bundle(self,
                              params: BundleParams,
                              sim_options: SimBundleOptions) -> str:
        """

        :param params: Bundle parameters
        :param sim_options: Simulation options
        :return: Transaction hash
        """
        first_tx = params['body'][0]
        if 'hash' in first_tx:
            print(
                "Transaction hash: " + first_tx['hash'] +
                " must appear onchain before simulation is possible, waiting"
            )
            if not self.w3_async:
                raise AttributeError("Node URL must be provided to simulate bundle")
            _ = await self.w3_async.eth.wait_for_transaction_receipt(first_tx['hash'])
            web3_tx = await self.w3_async.eth.get_transaction(first_tx['hash'])

            # RLP encode the transaction, throw error if type is not supported or arguments missing
            try:
                signed_tx = self._rlp_encode(web3_tx)
            except Exception as e: # pylint: disable=broad-except
                print(e)
                return

            print("Transaction hash: " + first_tx['hash']
                  + " confirmed, proceeding with simulation")
            sim_options['parent_block'] = sim_options['parent_block'] \
                if 'parent_block' in sim_options else web3_tx.blockNumber - 1
            params_with_signed_tx = params.copy()
            params_with_signed_tx['body'][0] = {'tx': signed_tx}

            return await self.__handle_request(
                [dict(munge_bundle_params(params_with_signed_tx)[0],
                      **munge_sim_bundle_options(sim_options))
                 ], "mev_simBundle")
        return await self.__handle_request(
            [
                dict(munge_bundle_params(params)[0],
                     **munge_sim_bundle_options(sim_options))
            ], "mev_simBundle")
