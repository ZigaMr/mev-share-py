"""
Unit tests for the SSE client
"""
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

from web3 import Web3
from aiounittest import AsyncTestCase
from mev_share_py.client import MevShareClient

# pylint: disable=duplicate-code
class MockServerHandler(BaseHTTPRequestHandler):
    """
    Mock server handler
    """
    # pylint: disable=invalid-name
    def do_GET(self): # pylint: disable=invalid-name
        """
        Mock server handler
        :return:
        """
        if self.path == "/api/v1/history/info":
            info = {
                "Count": 1,
                "MinBlock": 2,
                "MaxBlock": 3,
                "MinTimestamp": 4,
                "MaxLimit": 5,
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path.split('?')[0] == "/api/v1/history":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            history = [
                {
                    "block": 1,
                    "timestamp": 2,
                    "hint": {
                        "hash": "0x123"
                    }
                },
                {
                    "Block": 3,
                    "Timestamp": 4,
                    "Hint": {
                        "Hash": "0x123"
                    }
                }
            ]

            self.wfile.write(json.dumps(history).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
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

    def setUp(self):
        self.server_url = "http://localhost:8080"
        w3 = Web3(Web3.HTTPProvider('')) # pylint: disable=invalid-name
        account = w3.eth.account.create()  # Create a random wallet
        self.client = MevShareClient(rpc_url=self.server_url,
                                     stream_url=self.server_url,
                                     sign_key=account._private_key.hex(), # pylint: disable=protected-access
                                     node_url='')

    async def test_history(self):
        """
        Test the mock server by sending empty POST request
        :return:
        """

        response = await self.client.get_event_history_info()
        print(response)
        self.assertEqual(response['Count'], 1)
        self.assertEqual(response['MinBlock'], 2)
        self.assertEqual(response['MaxBlock'], 3)
        self.assertEqual(response['MinTimestamp'], 4)
        self.assertEqual(response['MaxLimit'], 5)

        response = await self.client.get_event_history(params={'blockStart': 1,
                                                               'blockEnd': 2,
                                                               'timestampStart': 3,
                                                               'timestampEnd': 4,
                                                               'offset': 5}
                                                       )
        self.assertEqual(response[0]['block'], 1)
        self.assertEqual(response[0]['timestamp'], 2)
        self.assertEqual(response[0]['hint']['hash'], '0x123')
