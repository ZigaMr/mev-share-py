"""
Test the mungers.
"""
import unittest
from mev_share_py.api.mungers import (
    munge_private_tx_params,
    munge_bundle_params,
    munge_sim_bundle_options,
)
from mev_share_py.api.types import (
    TransactionOptions,
    BundleParams,
    SimBundleOptions
)
# pylint: disable=duplicate-code
class TestMungers(unittest.TestCase):
    """
    Test the mungers.
    """

    def test_munge_private_tx_params(self):
        """
        Test that the private tx params are munged correctly.
        :return:
        """
        signed_tx = "0xabcdef"
        options: TransactionOptions = {
            'hints': {
                'calldata': True,
                'logs': True,
            },
            'max_block_number': 100,
            'builders': ['builder1', 'builder2'],
        }

        expected_result = [{
            'tx': signed_tx,
            'maxBlockNumber': '0x64',
            'preferences': {
                'fast': True,
                'privacy': {
                    'builders': ['builder1', 'builder2'],
                    'hints': ['calldata', 'logs', 'hash']
                }
            },
        }]

        result = munge_private_tx_params(signed_tx, options)

        self.assertEqual(result, expected_result)

    def test_munge_bundle_params(self):
        """
        Test that the bundle params are munged correctly.
        :return:
        """
        bundle_params: BundleParams = {
            'version': 'v0.1',
            'inclusion': {
                'block': 1,
                'max_block': 2,
            },
            'body': [{'hash': '0xabcdef'}, {'tx': '0x123456', 'canRevert': True}],
            'validity': [{'bodyIdx': 0, 'percent': 50}],
            'privacy': {
                'hints': {'calldata': True, 'logs': True},
                'builders': ['builder1', 'builder2'],
            },
            'metadata': {'originId': '12345'},
        }

        expected_result = [{
            'version': 'v0.1',
            'inclusion': {
                'block': '0x1',
                'maxBlock': '0x2',
            },
            'body': [{'hash': '0xabcdef'}, {'tx': '0x123456', 'canRevert': True}],
            'validity': [{'bodyIdx': 0, 'percent': 50}],
            'privacy': {
                'hints': ['calldata', 'logs', 'hash'],
                'builders': ['builder1', 'builder2'],
            },
        }]

        result = munge_bundle_params(bundle_params)

        self.assertEqual(result, expected_result)

    def test_munge_sim_bundle_options(self):
        """
        Test that the sim bundle options are munged correctly.
        :return:
        """
        sim_bundle_options: SimBundleOptions = {
            'parent_block': 1,
            'block_number': 100,
            'coinbase': 291,
            'timestamp': 1628500000,
            'gas_limit': 21000,
            'base_fee': 100,
            'timeout': 5,
        }

        expected_result = {
            'parentBlock': '0x1',
            'blockNumber': '0x64',
            'coinbase': 291,
            'timestamp': '0x6110f020',
            'gasLimit': '0x5208',
            'baseFee': '0x64',
            'timeout': 5,
        }

        result = munge_sim_bundle_options(sim_bundle_options)

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
