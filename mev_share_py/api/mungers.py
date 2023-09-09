from typing import Optional, Dict, List, TypedDict
from api.events import TransactionOptions



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

def extract_specified_hints(hints: HintPreferences) -> List[str]:
    return [key for key, value in munge_hint_preferences(hints).items() if value]

def munge_private_tx_params(signed_tx: str,
                            options: Optional[TransactionOptions] = None) -> List[Dict[str, any]]:
    params = {
        "tx": signed_tx,
        "maxBlockNumber": options['max_block_number'] if options and options['max_block_number'] else None,
        "preferences": {
            "fast": True,  # deprecated but required; setting has no effect
            # privacy uses the default (Stable) config if no hints specified
            "privacy": {"hints": extract_specified_hints(options.hints)} if options and options.hints else None,
            "builders": options.builders if options and options.builders else None,
        },
    }
    return [params]

def munge_bundle_params(params: BundleParams) -> Dict[str, any]:

    munged_bundle = [munge_bundle_params(item) for item in params["body"] if item["type"] == "bundle"]

    return {
        **params,
        "body": munged_bundle,
        "version": params.get("version", "v0.1"),
        "inclusion": {
            **params["inclusion"],
            "block": f"0x{params['inclusion']['block']:x}",
            "maxBlock": f"0x{params['inclusion']['maxBlock']:x}" if "maxBlock" in params["inclusion"] else None,
        },
        "validity": params.get("validity", {"refund": [], "refundConfig": []}),
        "privacy": {
            **params["privacy"],
            "hints": extract_specified_hints(params["privacy"]["hints"]) if "hints" in params["privacy"] else None,
        } if "privacy" in params else None
    }

def munge_sim_bundle_options(params: SimBundleOptions) -> Dict[str, any]:
    return {
        **params,
        "parentBlock": f"0x{params['parentBlock']:x}" if "parentBlock" in params else None,
        "blockNumber": f"0x{params['blockNumber']:x}" if "blockNumber" in params else None,
        "timestamp": f"0x{params['timestamp']:x}" if "timestamp" in params else None,
        "gasLimit": f"0x{params['gasLimit']:x}" if "gasLimit" in params else None,
        "baseFee": f"0x{params['baseFee']:x}" if "baseFee" in params else None,
    }
