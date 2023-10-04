# pylint: disable=missing-module-docstring
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from web3 import Web3

from aiounittest import AsyncTestCase
from mev_share_py.client import MevShareClient
from mev_share_py.api.types import BundleParams

# pylint: disable=duplicate-code
class MockServerHandler(BaseHTTPRequestHandler):
    """
    Mock server handler
    """
    def do_POST(self): # pylint: disable=invalid-name
        """
        Mock server handler
        :return:
        """
        if 'application/json' in self.headers.values() \
                and 'X-Flashbots-Signature' in self.headers.keys():
            response_data = {"status": "success"}
            response_json = json.dumps(response_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_json.encode())
        else:
            response_data = {"status": "error"}
            response_json = json.dumps(response_data)
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_json.encode())
        self.end_headers()


class TestMockServer(AsyncTestCase):
    """
    Test the mock server by sending empty POST request
    """
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("localhost", 8080), MockServerHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.socket.close()
        cls.server_thread.join()

    def setUp(self): # pylint: disable=invalid-name
        self.server_url = "http://localhost:8080"
        w3 = Web3(Web3.HTTPProvider('')) # pylint: disable=invalid-name
        account = w3.eth.account.create()  # Create a random wallet
        self.client = MevShareClient(rpc_url=self.server_url,
                                     stream_url=self.server_url,
                                     sign_key=account._private_key.hex(),  # pylint: disable=protected-access
                                     node_url='')

    async def test_mock_server(self):
        """
        Test the mock server by sending empty POST request
        :return:
        """
        # pylint: disable=no-member
        response = await self.client._RPCClient__handle_request([{}, {}], "test_method")  # pylint: disable=protected-access

        self.assertEqual(response['status'], 'success')

    async def test_public_methods(self):
        """
        Test sending a transaction to the mock server
        :return:
        """

        # Test sending a transaction to the mock server
        response = await self.client.send_transaction("0x123",
                                                      {'max_block_number': 10,
                                                       'hints': {
                                                           'calldata': True,
                                                           'contract_address': True,
                                                           'function_selector': True,
                                                           'logs': True
                                                       }
                                                       })
        self.assertEqual(response['status'], 'success')

        # Test sending a bundle
        params = {
            'inclusion': {
                'block': 1,
                'max_block': 10,
            },
            'body': [
                {'tx': '0x123', 'canRevert': True},
                {'tx': '0x123', 'canRevert': True}],
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
        response = await self.client.send_bundle(params)
        self.assertEqual(response['status'], 'success')

        # Test simulating a bundle
        params = {
            'inclusion': {
                'block': 1,
                'max_block': 10
            },
            'body': [{'tx': '0x123', 'canRevert': True},
                     {'tx': '0x123', 'canRevert': True}],
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
            'parent_block': 0,
        }
        params = BundleParams(**params)
        result = await self.client.simulate_bundle(params, sim_options)
        self.assertEqual(result['status'], 'success')
