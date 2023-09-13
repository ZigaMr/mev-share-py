from web3 import Web3, Account
from eth_account.messages import encode_defunct
import json
from typing import List, Dict


async def get_rpc_request(params: List,
                          method: str,
                          auth_signer: Account,
                          id_rpc: [str, int] = 5) -> Dict:
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
