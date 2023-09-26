import json
from typing import List, Dict

from eth_account.messages import encode_defunct
from web3 import Web3, Account


async def get_rpc_request(params: List,
                          method: str,
                          auth_signer: Account,
                          id_rpc: [str, int] = 5) -> Dict:
    """
    Generates a request for the Flashbots RPC endpoint.
    :param params: Parameters for the RPC request.
    :param method: Method for the RPC request.
    :param auth_signer: Account used to sign the request.
    :param id_rpc: RPC request ID.
    :return: Request headers, signature, and body.
    """
    body = {
        "jsonrpc": "2.0",
        "id": str(id_rpc),
        "params": params,
        "method": method,

    }
    message = encode_defunct(text=Web3.keccak(text=json.dumps(body)).hex())
    signature = auth_signer.address + ":" + auth_signer.sign_message(message).signature.hex()
    headers = {
        "Content-Type": "application/json",
        "X-Flashbots-Signature": signature,
    }
    return headers, signature, body
