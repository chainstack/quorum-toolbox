# coding=utf-8
import json

from quorumtoolbox.utils import ibft_utils
from quorumtoolbox.utils.node_utils import make_node_param


class Ibft:
    def __init__(self,
                 context,
                 enode_id_geth,  # e.g. 'enode://$enode@$geth_ip:$geth_port?discport=$discport'
                 node_state,  # 'initial' or 'new'
                 block_time=1,  # default value in quorum. mint blocks at this many seconds interval
                 peers=None):
        self.context = context
        self.enode_id_geth = enode_id_geth
        self.block_time = block_time
        self.node_state = node_state
        self.peers = [] if peers is None else peers

        self.init_node(self.node_state)

        # configuration related to this class instance
        self.build_config = {
            'ibft': {
                'block_time': self.block_time,
                'node_state': self.node_state
            },
            'enode_id_geth': self.enode_id_geth,
            'network': {
                'peers': self.peers
            }
        }

        # configuration related to launching this instance of ibft, used in cmd line args when launching geth.
        self.launch_params = {
            'istanbul_blockperiod': make_node_param('--istanbul.blockperiod', self.block_time),
            'syncmode': make_node_param('--syncmode', 'full'),
            'mine': '--mine',
            'minerthreads': make_node_param('--minerthreads', 1),
            'rpcapi': make_node_param('--rpcapi', 'istanbul')
        }

    def init_node(self, node_state):
        {
            'initial_ibft': self.init_initial,
            'new_ibft': self.init_new
        }[node_state]()

    # This node is forming the initial network. Nothing to do.
    def init_initial(self):
        pass

    # This node is new to the network and it needs to be added to existing network
    def init_new(self):
        self.join_existing_ibft_network()

    # No joining id for ibft
    @property
    def joining_id(self):
        return None

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def launch_parameters(self):
        return self.launch_params

    def join_existing_ibft_network(self):
        ibft_utils.join_existing_ibft_network(self.peers, self.enode_id_geth)

    def __str__(self):
        return json.dumps(self.build_config)
