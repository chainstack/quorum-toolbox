import os
import random

from quorumtoolbox.quorum_network import QuorumNetwork
from quorumtoolbox.utils import fs_utils


# This class is used to create a single Quorum node- either Initial or New node.
# See test_create_quorum_node.py to see how this works.
class CreateQuorumNode:
    def __init__(self, node_params, network_params={}):
        other_raft_public_ip = network_params.get('other_raft_public_ip', None)
        other_constellation_public_ip = network_params.get('other_constellation_public_ip', None)

        self.genesis = network_params.get('genesis_content', '')

        self.constellation_params = {
            'other_nodes': [other_constellation_public_ip] if other_constellation_public_ip is not None else []
        }

        self.raft_params = {
            'peers': [other_raft_public_ip] if other_raft_public_ip is not None else []
        }

        self.geth_params = {
            'max_peers': 250
        }

        if node_params.get('networkid', None) is None:
            self._networkid = random.randint(100, 100000)
        else:
            self._networkid = node_params['networkid']

        self.context = node_params['context']
        self.address = node_params['address']
        self.node_state = node_params['node_state']

        self.create_context()

        self.qn = QuorumNetwork(1,
                                self._networkid,
                                [self.context],
                                [self.address],
                                ['0.0.0.0'],
                                self.node_state,
                                genesis_content=self.genesis,
                                geth_params=self.geth_params,
                                consensus_params=self.raft_params,
                                private_manager_params=self.constellation_params)

        self._genesis_files = self.qn.build_configuration['local']['genesis_files']
        self._consensus_ids = self.qn.build_configuration['network']['consensus_ids']
        self._ptm_peers = self.qn.build_configuration['network']['private_manager_peers']
        self._ptm_urls = self.qn.build_configuration['network']['private_manager_urls']

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
    def ptm_url(self):
        return self._ptm_urls[0]

    @property
    def ptm_peers(self):
        return self._ptm_peers[0]

    def create_context(self):
        try:
            fs_utils.del_dir(self.context)
        except FileNotFoundError:
            pass

        fs_utils.copy_dir(os.path.dirname(os.path.abspath(__file__)) + '/template_dir', self.context)
