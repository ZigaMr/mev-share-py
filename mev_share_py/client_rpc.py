from web3 import Web3, Account
import requests
from flashbots_signature import get_rpc_request

class RPCClient:
    def __init__(self,
                 api_url: str = "https://api.mev-share.com/api/v1/",
                 # TODO: remove hardcoded mainnet url for safety reasons
                 private_key: str = None):
        self.api_url = api_url
        self.account = Account.from_key(private_key) if private_key else None


    async def __handle_request(self,
                             params,
                              method):
        headers, signature, body = await get_rpc_request(params, method, self.account)
        return requests.post(url=self.api_url, data=body,headers=headers).json()

    async def on_transaction(self):