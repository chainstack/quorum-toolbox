import json
import os

import raft_utils
from utils import templating
from utils.utils import make_param
from utils.enode_utils import make_enode_id2


class Raft:
    raft_dir_name = "raft"

    raft_id_file_name = "raftid.json"

    def __init__(self,
                 context,
                 enode_id_geth,  # e.g. "enode://$enode@$geth_ip:$geth_port?discport=$discport"
                 node_state,     # "initial" or "new"
                 port=50400,     # default value in quorum. need to make enode_id.
                 block_time=50,  # default value in quorum
                 peers=[]):

        self.context = context
        self.enode_id_geth = enode_id_geth
        self.port = port
        self.enode_id = make_enode_id2(self.enode_id_geth, self.port)
        self.block_time = block_time
        self.peers = peers
        self.node_state = node_state
        self._raft_id = None

        {
            'initial': self.init_initial,
            'new': self.init_new
        }[self.node_state]()

        self.base_dir = os.path.join(context, self.raft_dir_name)
        self.raft_id_file = os.path.join(self.base_dir, self.raft_id_file_name)

        self.write_raft_id()

        # configuration related to this class instance
        self.build_config = {
            'raft': {
                'block_time': self.block_time,
                'raft_id': self._raft_id,
                'node_state': self.node_state
            },
            'enode_id': self.enode_id,
            'network': {
                'port': self.port,
                'peers': self.peers
            },
            'local': {
                'raft_id_file': self.raft_id_file
            }
        }

        # configuration related to launching this instance of raft, used in cmd line args when launching geth.
        # https://github.com/jpmorganchase/quorum/blob/master/raft/doc.md
        self.launch_params = {
            'raft': "--raft",
            'rpcapi': make_param("--rpcapi", "raft"),
            'raftport': make_param("--raftport", self.port),
            'raftblocktime': make_param("--raftblocktime", self.block_time)     # mint blocks in this many millisecond interval
        }

        if self._raft_id is not None:
            self.launch_params['raftjoinexisting'] = make_param("--raftjoinexisting", self._raft_id)     # join an existing network with this id

    # This node is forming the initial network. RAFT_ID will be automatically assigned by network (based on static-nodes
    # .json). so, don't bother.
    def init_initial(self):
        self._raft_id = None

    # This node is new to the network and a raft joining id has to be retrieved from peers.
    def init_new(self):
        self._raft_id = self.get_raft_id()

    @property
    def joining_id(self):
        return self._raft_id

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def launch_parameters(self):
        return self.launch_params

    def get_raft_id(self):
        return self.get_raft_joining_id()

    def write_raft_id(self):
        if self._raft_id is not None:
            templating.template_substitute(self.raft_id_file, {'raft_id': self._raft_id})
        else:
            templating.template_substitute(self.raft_id_file, {'raft_id': 'null'})

    def get_raft_joining_id(self):
        raft_joining_id = raft_utils.get_raft_joining_id(self.peers, self.enode_id)
        return raft_joining_id

    def sanity_check(self):
        pass

    def __str__(self):
        return json.dumps(self.build_config)

    def __repr__(self):
        pass
