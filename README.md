# mev-share-py

Client library that interacts with MEV-Share node written in Python 3.10.

Based on [MEV-Share](#https://github.com/flashbots/mev-share).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Features](#features)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [FAQs](#faqs)
- [Troubleshooting](#troubleshooting)
- [Contact](#contact)

## Installation

This repo assumes Python ^3.8. Preferred way is to use ```pyenv``` and ```poetry``` for managing Python versions and
dependencies.
Make sure to have both installed on your system. In case of other environment managers,
make sure to install the dependencies listed in ```pyproject.toml```.

Create poetry environment and install dependencies (change directory to the root of the repo):

```bash
# If using pyenv and poetry
pyenv install 3.10
pyenv local 3.10
poetry install
```

## Usage

Add the necessary variables to the config.json file.

```bash
{
  "relay_url_mainnet": "https://relay.flashbots.net",
  "sse_url_mainnet": "https://mev-share.flashbots.net/",
  "relay_url_goerli": "https://relay-goerli.flashbots.net/",
  "sse_url_goerli": "https://mev-share-goerli.flashbots.net/",
  "infura_key": "<your_infura_key>",
  "private_key": "<your_private_key>",
  "sign_key": "<your_sign_key>",
  "to": "<your_wallet_address>",
}
```

Import the client and create an instance of the client with the desired network.

```python
from client import MevShareClient

api_url = "https://relay-goerli.flashbots.net/"
stream_url = "https://mev-share-goerli.flashbots.net/"
client = MevShareClient(api_url=api_url, stream_url=stream_url)
```

## Usage

Client library uses python typeddict to define the types of the data for static analysis.
Those are not enforced at runtime. So make sure to check the types of parameters and return values.
The types are defined in ```api/events.py```.

The library consists of two main parts:

- RPC client that interacts with the MEV-Share node
- SSE client that listens for events from the MEV-Share node
- MevShareClient is a wrapper around both clients.

The library exposes the following public methods:

### listen_for_events

Subscribe to the event stream and listen for events of a specific type.
The method expects type of event (transaction/bundle) and a callback function that will be called when an event is
received.

```python
import asyncio
from client import MevShareClient
from api.events import PendingBundle, PendingTransaction


def callback_function(event: PendingTransaction):
    print(event)


client = MevShareClient()
res = asyncio.run(
    client.listen_for_events('transaction', callback_function),
)

```

### send_transaction

Send a private transaction to the MEV-Share node. Hints and options are passed as a dictionary.

```python
import asyncio
import json
from client import MevShareClient
from web3 import Web3

config = json.load(open('config.json'))

infura_http_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])
web3 = Web3(Web3.HTTPProvider(infura_http_url))
raw_tx = '<raw_tx>'  # Add raw tx here


async def send_tx(tx: str):
    client = MevShareClient()
    print(tx)
    return await client.send_transaction(tx.rawTransaction.hex(),
                                         {'max_block_number': web3.eth.block_number + 10,
                                          'hints': {
                                              'calldata': True,
                                              'logs': True,
                                              'function_selector': True,
                                              'hash': True,
                                              'tx_hash': True
                                          }
                                          }
                                         )


if __name__ == "__main__":
    tx = asyncio.run(send_tx(raw_tx))
    print(tx)
```

### send_bundle
Sends a bundle of transactions to the MEV-Share node. Hints and options are passed as a dictionary.
See [MEV-Share Docs](#https://github.com/flashbots/mev-share/blob/main/src/mev_sendBundle.md) for detailed descriptions of these parameters.

When sending bundles containing only signed transactions, 
we can share hints by uncommenting the privacy section.

```python
import asyncio
import json
from web3 import Web3
from api.types import BundleParams
from client import MevShareClient
from api.events import PendingTransaction

config = json.load(open('config.json'))

infura_ws_url = "wss://goerli.infura.io/ws/v3/{}".format(config['infura_key'])
infura_http_url = "https://goerli.infura.io/v3/{}".format(config['infura_key'])
web3 = Web3(Web3.HTTPProvider(infura_http_url))


async def build_and_send(tx1: PendingTransaction):
    tx2 = '0x'  # Add raw tx here
    params = {
        'inclusion': {
            'block': web3.eth.block_number + 1,
            # 'max_block': web3.eth.block_number+10,
        },
        'body': [{'hash': tx1.hash},
                 {'tx': tx2}],
        # 'privacy': {
        #     'hints': {
        #         'tx_hash': True,
        #         'calldata': True,
        #         'logs': True,
        #         'function_selector': True,
        #     },
        #     # 'builders': ['flashbots']
        # }
    }
    params = BundleParams(**params)
    return await client.send_bundle(params)


client = MevShareClient()
res = asyncio.run(
    client.listen_for_events('transaction', build_and_send)
)

```

### simulate_bundle
[Simulates](#https://docs.flashbots.net/flashbots-mev-share/searchers/debugging#simulate-your-bundle) a bundle.
Similar to send_bundle, but also accepts options to modify block header.

```python

TARGET_BLOCK = web3.eth.block_number + 1
params = {
    'inclusion': {
        'block': TARGET_BLOCK,
        'max_block': TARGET_BLOCK + 10,
    },
    'body': [{'hash': txHash, 'canRevert': True},
             {'tx': tx2.rawTransaction.hex(), 'canRevert': True}],
    'privacy': {
        'hints': {
            'tx_hash': True,
            'calldata': True,
            'logs': True,
            'function_selector': True,
        },
        # 'builders': ['flashbots']
    }
}
sim_options = {
    'parent_block': TARGET_BLOCK - 1,
    # 'block_number': Optional[int],
    # 'coinbase': Optional[str],
    # 'timestamp': Optional[int],
    # 'gas_limit': Optional[int],
    # 'base_fee': Optional[int],
    # 'timeout': Optional[int],
}
params = BundleParams(**params)
await client.simulate_bundle(params, sim_options)
```


### get_event_history_info
Get information about the event history endpoint for use in get_event_history.

```python
client = MevShareClient(stream_url=STREAM_URL)
his_info = asyncio.run(client.get_event_history_info())
```
Returns a dictionary:
```python
{
    'count': 2996044,
    'minBlock': 9091377,
    'maxBlock': 9734719,
    'minTimestamp': 1685452445,
    'maxTimestamp': 1695313814,
    'maxLimit': 500
}
```

### get_event_history
Get historical event stream data for last 100 blocks.

```python
params = {"blockStart": his_info['maxBlock'] - 100, "blockEnd": his_info['maxBlock']}
his = asyncio.run(client.get_event_history(params=params))
```

## Examples
All examples are located in the [```examples```](#/examples) directory.
## Contributing

## License

This project is licensed under the MIT License.

## Acknowledgments

## FAQs

## Troubleshooting

## Contact

For questions or feedback, contact ziga.mrzljak@gmail.com