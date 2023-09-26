from typing import Optional, Dict, List
from mev_share_py.api.types import TransactionOptions, BundleParams


def munge_private_tx_params(signed_tx: str,
                            options: Optional[TransactionOptions] = None) -> List[Dict[str, any]]:
    """
    Munge private transaction parameters into the format expected by the RPC.
    :param signed_tx:
    :param options:
    :return:
    """
    params = {
        "tx": signed_tx,
        "maxBlockNumber": hex(options.get('max_block_number')) if options else None,
        "preferences": {
            "fast": True,  # deprecated but required; setting has no effect
            # privacy uses the default (Stable) config if no hints specified
            "privacy":
                {
                    "hints": [k for k, v in dict(options.get('hints'), **{'hash': True}).items() if
                              v] if options and options.get('hints') else None,
                    "builders": options.get('builders') if options else None
                }

        },
    }
    return [params]


def munge_bundle_params(params: BundleParams) -> List[Dict[str, any]]:
    """
    Munge bundle parameters into the format expected by the RPC.
    :param params:
    :return:
    """
    munged_bundle = [{'bundle': munge_bundle_params(item)}
                     if "bundle" in item.keys() else item
                     for item in params.get("body")]

    return [{
        "version": params.get("version", "v0.1"),
        "inclusion": {
            "block": f"0x{params['inclusion']['block']:x}",
            "maxBlock":
                f"0x{params['inclusion']['max_block']:x}"
                if "max_block" in params["inclusion"] else None,
        },
        "body": munged_bundle,
        "validity": params.get("validity", {"refund": [], "refundConfig": []}),
        "privacy":
            {
                "hints":
                    [k for k, v in dict(params["privacy"].get('hints'),
                                        **{'hash': True}).items() if v]
                    if params["privacy"] and params["privacy"].get('hints') else None,
                "builders": params["privacy"].get('builders') if params["privacy"] else None
            }
    }]


def munge_sim_bundle_options(params) -> Dict[str, any]:
    """
    Transforms python notation simulation options into the format expected by the MEV-Share API
    :param params:
    :return:
    """
    return {
        "parentBlock": hex(params['parent_block']) if "parent_block" in params else None,
        "blockNumber": hex(params['block_number']) if "block_number" in params else None,
        "coinbase": params['coinbase'] if "coinbase" in params else None,
        "timestamp": hex(params['timestamp']) if "timestamp" in params else None,
        "gasLimit": hex(params['gas_limit']) if "gas_limit" in params else None,
        "baseFee": hex(params['base_fee']) if "base_fee" in params else None,
        "timeout": params['timeout'] if "timeout" in params else None,
    }
