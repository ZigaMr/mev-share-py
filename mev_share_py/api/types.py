from typing import List, Optional, TypedDict, NewType, Union, Dict, Any, Callable

HintPreferences = TypedDict(
    'HintPreferences',
    {
        'calldata': Optional[bool],
        'contract_address': Optional[bool],
        'function_selector': Optional[bool],
        'logs': Optional[bool],
        'tx_hash': Optional[bool]
    }
)

TransactionOptions = TypedDict(
    'TransactionOptions',
    {
        'hints': Optional[HintPreferences],
        'max_block_number': Optional[int],
        'builders': Optional[List[str]]
    }
)

HashItem = TypedDict(
    'HashItem',
    {
        'hash': str,
    }
)

TxItem = TypedDict(
    'TxItem',
    {
        'tx': str,
        'canRevert': bool
    }
)

BundleItem = TypedDict(
    'BundleItem',
    {
        'bundle': 'BundleParams'
    }
)

Inclusion = TypedDict(
    'Inclusion',
    {
        'block': str,
        'max_block': Optional[str]
    }
)

Refund = TypedDict(
    'Refund',
    {
        'bodyIdx': int,
        'percent': int
    }
)

RefundConfig = TypedDict(
    'RefundConfig',
    {
        'address': str,
        'percent': int
    }
)

Privacy = TypedDict(
    'Privacy',
    {
        'hints': HintPreferences,
        'builders': List[str],
    }
)

MetaData = TypedDict(
    'MetaData',
    {
        'originId': str,
    }
)

BundleParams = TypedDict(
    'BundleParams',
    {
        'version': Optional[str],
        'inclusion': Inclusion,
        'body': List[Union[HashItem, TxItem, BundleItem]],
        'validity': Optional[Union[List[Refund], List[RefundConfig]]],
        'privacy': Optional[Privacy],
        'metadata': MetaData
    }
)

SimBundleOptions = TypedDict(
    'SimBundleOptions',
    {
        'parent_block': Optional[Union[str, int]],
        'block_number': Optional[int],
        'coinbase': Optional[str],
        'timestamp': Optional[int],
        'gas_limit': Optional[int],
        'base_fee': Optional[int],
        'timeout': Optional[int],
    }
)