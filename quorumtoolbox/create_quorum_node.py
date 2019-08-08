# coding=utf-8
import os
import random

from quorumtoolbox.quorum_network import QuorumNetwork
from quorumtoolbox.utils import fs_utils, node_utils

""" This class is used to create a single Quorum node-
1. Initial or New Raft node
2. Initial or New IBFT node
See test_create_quorum_node.py to see how this works.
"""


class CreateQuorumNode:
    def __init__(self, node_params, network_params=None):
        network_params = {} if network_params is None else network_params

        self.sanity_checks(node_params, network_params)
        self.context = node_params['context']
        self.address = node_params['address']
        self.node_state = node_params['node_state']
        self.private_manager = node_params.get('private_manager', 'constellation')
        self._networkid = random.randint(100, 100000) if 'networkid' not in node_params else node_params['networkid']

        self.geth_params = {
            'max_peers': 250
        }

        self.genesis = ''
        self.consensus_params = {
            'peers': []
        }
        self.ptm_params = {
            'other_nodes': []
        }

        if node_utils.is_new_node(node_params['node_state']):
            self.genesis = network_params['genesis_content']
            self.consensus_params = {
                'peers': [network_params['other_node_public_ip']]
            }
            self.ptm_params = {
                'other_nodes': [network_params['other_ptm_public_ip']]
            }

        self.create_context()

        self.qn = QuorumNetwork(1,
                                self._networkid,
                                [self.context],
                                [self.address],
                                ['0.0.0.0'],
                                self.node_state,
                                private_manager=self.private_manager,
                                genesis_content=self.genesis,
                                geth_params=self.geth_params,
                                consensus_params=self.consensus_params,
                                private_manager_params=self.ptm_params)

        self._genesis_files = self.qn.build_configuration['local']['genesis_files']
        self._consensus_ids = self.qn.consensus_ids
        self._enode_ids = self.qn.enode_ids
        self._ibft_addresses = self.qn.ibft_addresses
        self._ptm_peers = self.qn.private_manager_peers
        self._ptm_urls = self.qn.private_manager_urls
        self._ptm_addresses = self.qn.private_manager_addresses

    @property
    def genesis_content(self):
        return open(self._genesis_files[0], 'r').read()

    @property
    def networkid(self):
        return self._networkid

    @property
    def consensus_id(self):
        return self._consensus_ids[0]

    @property
    def enode_id(self):
        return self._enode_ids[0]

    @property
    def ibft_address(self):
        return self._ibft_addresses[0]

    @property
    def ptm_url(self):
        return self._ptm_urls[0]

    @property
    def ptm_address(self):
        return self._ptm_addresses[0]

    @property
    def ptm_peers(self):
        return self._ptm_peers[0]

    def create_context(self):
        try:
            fs_utils.del_dir(self.context)
        except FileNotFoundError:
            pass

        fs_utils.copy_dir(os.path.dirname(os.path.abspath(__file__)) + '/template_dir', self.context)

    def sanity_checks(self, node_params, network_params):
        self.sanity_checks_common(node_params)

        if node_utils.is_new_node(node_params['node_state']):
            self.sanity_checks_new_node(network_params)

        # no further checks for initial node

    @staticmethod
    def sanity_checks_common(node_params):
        if not node_params.get('context'):
            raise Exception('Error, context parameter not provided')

        if not node_params.get('address'):
            raise Exception('Error, address parameter not provided')

        node_state = node_params.get('node_state', None)
        private_manager = node_params.get('private_manager', None)

        if not node_state or not node_utils.is_raft_or_istanbul_node(node_state):
            raise Exception('Error, node_state parameter not provided, or it is wrong')

        if not private_manager or not node_utils.is_constellation_or_tessera_node(private_manager):
            raise Exception('Error, private_manager parameter not provided, or it is wrong')

    @staticmethod
    def sanity_checks_new_node(network_params):
        if not network_params.get('genesis_content'):
            raise Exception('Error, genesis_content parameter not provided')

        if not network_params.get('other_node_public_ip'):
            raise Exception('Error, other_node_public_ip parameter not provided')

        if not network_params.get('other_ptm_public_ip'):
            raise Exception('Error, other_ptm_public_ip parameter not provided')
