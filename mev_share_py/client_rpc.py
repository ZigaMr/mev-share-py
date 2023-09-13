from web3 import Web3, Account, eth
from web3.datastructures import AttributeDict
from rlp import encode
from eth_utils import to_bytes
import asyncio
import requests
import json
from flashbots_signature import get_rpc_request
from web3.types import SignedTx
from api.types import TransactionOptions, BundleParams, SimBundleOptions
from typing import Dict, Any, List, Callable, Union
from api.mungers import munge_private_tx_params, munge_bundle_params, munge_sim_bundle_options


class RPCClient:
    def __init__(self,
                 api_url: str = "https://api.mev-share.com/api/v1/",
                 # TODO: remove hardcoded mainnet url for safety reasons
                 private_key: str = None,
                 node_url: str = None):
        self.api_url = api_url
        self.account = Account.from_key(private_key) if private_key else None
        self.w3 = Web3(Web3.HTTPProvider(node_url)) if node_url else None
        self.w3_async = Web3(Web3.AsyncHTTPProvider(node_url), modules={'eth': (eth.AsyncEth,)}, middlewares=[])

    async def __handle_request(self,
                               params,
                               method):
        headers, signature, body = await get_rpc_request(params,
                                                         method,
                                                         self.account,
                                                         "1")
        print(json.dumps(body))
        return requests.post(url=self.api_url, data=json.dumps(body), headers=headers).json()

    def _rlp_encode(self, tx: AttributeDict):
        """
        RLP encodes a transaction since get_raw_transaction() is not available on most public nodes.
        :param tx: Transaction object
        :return: RLP encoded signed transaction (hex string)
        """

        to_as_bytes = to_bytes(hexstr=tx["to"])
        encoded_tx = "0x02" + encode(
            [tx['chainId'], tx['nonce'], tx['maxPriorityFeePerGas'], tx['maxFeePerGas'], tx['gas'], to_as_bytes,
             tx['value'], tx['input'], tx['accessList'], tx['v'], tx['r'], tx['s']]).hex()
        return encoded_tx

    async def send_transaction(self,
                               signed_tx: str,
                               options: TransactionOptions) -> str:
        """

        :param signed_tx:
        :param options:
        :return:
        """
        munger_params = munge_private_tx_params(signed_tx, options)
        # res = await self.__handle_request(munger_params, "eth_sendRawTransaction")
        return await self.__handle_request(munger_params, "eth_sendPrivateTransaction")

    async def send_bundle(self, params: BundleParams) -> str:
        """
        
        :param params: 
        :return: 
        """
        munger_params = munge_bundle_params(params)
        # res = await self.__handle_request(munger_params, "eth_sendRawTransaction")
        return await self.__handle_request(munger_params, "mev_sendBundle")

    async def simulate_bundle(self,
                              params: BundleParams,
                              sim_options: SimBundleOptions,
                              timeout_seconds: int = 60) -> str:
        """

        :param params:
        :param sim_options:
        :return:
        """
        first_tx = params['body'][0]
        if 'hash' in first_tx:
            print(
                "Transaction hash: " + first_tx['hash'] + " must appear onchain before simulation is possible, waiting")
            if not self.w3_async:
                raise Exception("Node URL must be provided to simulate bundle")
            tx = self.w3.eth.wait_for_transaction_receipt(first_tx['hash'], timeout=timeout_seconds)
            tx = await self.w3_async.eth.get_transaction(first_tx['hash'])
            signed_tx = self._rlp_encode(tx)
            # if tx.status != 1:
            #     raise AssertionError("Transaction failed")
            print("Transaction hash: " + first_tx['hash'] + " confirmed, proceeding with simulation")
            sim_options['parent_block'] = sim_options['parent_block'] if 'parent_block' in sim_options else tx.blockNumber - 1
            params_with_signed_tx = params.copy()
            params_with_signed_tx['body'][0] = {'tx': signed_tx}

            return await self.__handle_request([dict(munge_bundle_params(params_with_signed_tx)[0],
                                                     **munge_sim_bundle_options(sim_options))], "mev_simulateBundle")
        return await self.__handle_request([dict(munge_bundle_params(params)[0],
                                                 **munge_sim_bundle_options(sim_options))], "mev_simulateBundle")
