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

There are two ways to initalize the client:

#### 1) Using the constructor:
(throws an error if any keyword argument is missing):
```bash
from client import MevShareClient
client = MevShareClient(api_url='https://relay.flashbots.net/', 
                        sign_key='<your_sign_key>',
                        node_url='https://goerli.infura.io/v3/<your_infura_key>',
                        stream_url='https://mev-share.flashbots.net/')
                        )
```

#### 2) Using the classmethod ```from_config``` which reads from the head dir config.json file:
For this to work, you need to pass the network string (currently either 'goerli' or 'mainnet') and config.json file path to the classmethod.
The ```private_key``` and ```to``` fields are optional, used for easy access by accessing the client.config parameter.
The private_key is only used in the example files. 
### It is NOT advisable to store your PROD private key in the config file.
Add the necessary variables to the config.json file.

```bash
{
  "mainnet": {
    "relay_url": "https://relay.flashbots.net",
    "sse_url": "https://mev-share.flashbots.net/",
    "infura_url": "https://mainnet.infura.io/v3/{}"
  },
  "goerli": {
    "relay_url": "https://relay-goerli.flashbots.net/",
    "sse_url": "https://mev-share-goerli.flashbots.net/",
    "infura_url": "https://goerli.infura.io/v3/{}"
  },
  "infura_key": "<your_infura_key>",
  "private_key": "<your_private_key>",
  "sign_key": "<your_sign_key>",
  "to": "<your_wallet_address>",
}
```
Import the client and create an instance of the client with the desired network.

```bash
from client import MevShareClient
client = MevShareClient.from_config('goerli', '../config.json')
```


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
from mev_share_py.client import MevShareClient
from api.events import PendingTransaction


def callback_function(event: PendingTransaction):
    print(event)


client = MevShareClient.from_config('goerli', '../config.json')
res = asyncio.run(
    client.listen_for_events('transaction', callback_function),
)

```

### send_transaction

Send a private transaction to the MEV-Share node. Hints and options are passed as a dictionary.

```python
import asyncio
from mev_share_py.client import MevShareClient

raw_tx = '<raw_tx>'  # Add raw tx here


async def send_tx(tx: str):
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    print(tx)
    return await client.send_transaction(
        tx.rawTransaction.hex(),
        {
            'max_block_number': await client.w3_async.eth.block_number + 10,
            'hints': {
                'calldata': True,
                'contract_address': True,
                'function_selector': True,
                'logs': True
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
from mev_share_py.client import MevShareClient
from mev_share_py.api.types import BundleParams



async def build_and_send():
    """
    Generate a bundle with two private transactions and send it.
    :return:
    """
    tx1 = '<raw_tx1>'
    tx2 = '<raw_tx2>'
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    tx1 = tx1
    tx2 = tx2
    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 10,
        },
        'body': [
            {'tx': tx1.rawTransaction.hex()},
            {'tx': tx2.rawTransaction.hex()}],
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
    params = BundleParams(**params)
    print(await client.send_bundle(params))

if __name__ == "__main__":
    asyncio.run(build_and_send())
```

### simulate_bundle
[Simulates](#https://docs.flashbots.net/flashbots-mev-share/searchers/debugging#simulate-your-bundle) a bundle.
Similar to send_bundle, but also accepts options to modify block header.

```python
import asyncio
from mev_share_py.api.types import BundleParams
from mev_share_py.client import MevShareClient


async def sim_private_tx_backrun():
    """
    Generate a bundle with two private transactions and simulate it.
    The "to" address and "private_key" are read from the config.json file.
    :return:
    """
    tx1 = '<raw_tx1>'
    tx2 = '<raw_tx2>'
    client = MevShareClient.from_config(network='goerli', config_dir='../config.json')
    tx1 = tx1
    tx2 = tx2
    block_number = await client.w3_async.eth.block_number
    params = {
        'inclusion': {
            'block': block_number + 1,
            'max_block': block_number + 10
        },
        'body': [{'tx': tx1.rawTransaction.hex(), 'canRevert': True},
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
        'parent_block': block_number,
    }
    params = BundleParams(**params)
    return await client.simulate_bundle(params, sim_options)

if __name__ == "__main__":
    res = asyncio.run(sim_private_tx_backrun())
    print(res)

```


### get_event_history_info
Get information about the event history endpoint for use in get_event_history.

```python
import asyncio
from mev_share_py.client import MevShareClient
client = MevShareClient.from_config('goerli', '../config.json')
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
params = {"blockStart": his_info['maxBlock'] - 1, "blockEnd": his_info['maxBlock']}
his = asyncio.run(client.get_event_history(params=params))
```

## Examples
All examples are located in the [```examples```](#/examples) directory.
## Contributing

## License

MIT License

Copyright (c) 2023 Žiga Mrzljak / Flashbots

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Acknowledgments

## FAQs

## Troubleshooting

## Contact

For questions or feedback, contact ziga.mrzljak@gmail.com