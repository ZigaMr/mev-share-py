from typing import Optional, Dict, List, TypedDict
from api.types import TransactionOptions, HintPreferences, BundleParams


def munge_hint_preferences(hints: HintPreferences) -> Dict[str, any]:
    return {
        "contract_address": hints.contractAddress,
        "function_selector": hints.functionSelector,
        "calldata": hints.calldata,
        "logs": hints.logs,
        "tx_hash": hints.txHash,
        "hash": True,  # tx hash is always shared on Flashbots MEV-Share; abstract away from the user
        # setting all hints except hash to False will enable full privacy
    }


def munge_private_tx_params(signed_tx: str,
                            options: Optional[TransactionOptions] = None) -> List[Dict[str, any]]:
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
    # if options and options.get('max_block_number'):
    #     params["maxBlockNumber"] = hex(options.get('max_block_number'))
    # if options and options.get('hints'):
    #     params["preferences"]["privacy"] = {"hints": [k for k, v in options.get('hints').items() if v]}
    # if options and options.get('builders'):
    #     params["preferences"]["builders"] = options.get('builders')
    return [params]


def munge_bundle_params(params: BundleParams) -> List[Dict[str, any]]:
    munged_bundle = [{'bundle': munge_bundle_params(item)} if "bundle" in item.keys() else item for item in
                     params.get("body")]

    return [{
        # **params,
        "version": params.get("version", "v0.1"),
        "inclusion": {
            # **params["inclusion"],
            "block": f"0x{params['inclusion']['block']:x}",
            "maxBlock": f"0x{params['inclusion']['max_block']:x}" if "max_block" in params["inclusion"] else None,
        },
        "body": munged_bundle,
        "validity": params.get("validity", {"refund": [], "refundConfig": []}),
        "privacy":
            {
                "hints": [k for k, v in dict(params["privacy"].get('hints'), **{'hash': True}).items() if
                          v] if params["privacy"] and params["privacy"].get('hints') else None,
                "builders": params["privacy"].get('builders') if params["privacy"] else None
            }
    }]


def munge_sim_bundle_options(params) -> Dict[str, any]:
    return {
        "parentBlock": hex(params['parentBlock']) if "parentBlock" in params else None,
        "blockNumber": hex(params['blockNumber']) if "blockNumber" in params else None,
        "coinbase": params['coinbase'] if "coinbase" in params else None,
        "timestamp": hex(params['timestamp']) if "timestamp" in params else None,
        "gasLimit": hex(params['gasLimit']) if "gasLimit" in params else None,
        "baseFee": hex(params['baseFee']) if "baseFee" in params else None,
        "timeout": hex(params['timeout']) if "timeout" in params else None,
    }
