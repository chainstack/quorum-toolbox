import os

from quorumtoolbox.constellation import Constellation
from quorumtoolbox.tessera import Tessera
from quorumtoolbox.geth import Geth
from quorumtoolbox.ibft import Ibft
from quorumtoolbox.raft import Raft
from quorumtoolbox.utils import enode_utils, bash_utils, node_utils


class QuorumNode:
    blockchain_dir_name = 'blockchain'
    quorum_node_config_file_name = 'quorum_node_config.sh'

    def __init__(self,
                 context,
                 address,
                 rpcaddr,
                 networkid,
                 node_state,
                 private_manager='constellation',
                 geth_params=None,
                 consensus_params=None,
                 private_manager_params=None):
        self.base_dir = os.path.join(context, self.blockchain_dir_name)
        self.quorum_node_config_file = os.path.join(self.base_dir, self.quorum_node_config_file_name)

        self.node_state = node_state

        geth_params = {} if geth_params is None else geth_params
        consensus_params = {} if consensus_params is None else consensus_params
        private_manager_params = {} if private_manager_params is None else private_manager_params

        self.geth = Geth(context, address, rpcaddr, networkid, **geth_params)

        if node_utils.is_raft_node(self.node_state):
            self.consensus = Raft(context, self.geth.enode_id_geth, node_state, **consensus_params)
        else:
            self.consensus = Ibft(context, self.geth.enode_id_geth, node_state, **consensus_params)

        if private_manager.lower() == 'constellation':
            self.private_manager = Constellation(context, address, **private_manager_params)
        else:
            self.private_manager = Tessera(context, address, **private_manager_params)

        # make the node's enode_id depending on consensus
        self._enode_id = self.make_enode_id_from_geth() if node_utils.is_raft_node(self.node_state) else \
            self.geth.enode_id_geth

        self._ibft_address, self._nodekey = self.geth.ibft_address, self.geth.nodekey

        # get launch params from components, combine to launch this node
        self.launch_params = bash_utils.make_quorum_node_launch_params([self.geth.launch_parameters,
                                                                        self.consensus.launch_parameters,
                                                                        self.private_manager.launch_parameters
                                                                        ])

        bash_utils.write_quorum_node_launch_config(self.launch_params, self.quorum_node_config_file)

        self.build_config = {
            'local': {
                'config_file': self.quorum_node_config_file
            },

            'geth': self.geth.build_configuration,
            'consensus': self.consensus.build_configuration,
            'private_manager': self.private_manager.build_configuration
        }

    def make_enode_id_from_geth(self):
        return enode_utils.make_enode_id2(self.geth.enode_id_geth,
                                          self.consensus.build_configuration['network']['port'])

    @property
    def launch_parameters(self):
        return self.launch_parameters

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def ibft_address(self):
        return self._ibft_address

    @property
    def enode_id(self):
        return self._enode_id

    @property
    def nodekey(self):
        return self._nodekey

    @property
    def accounts(self):
        return self.geth.accounts

    # TODO Formalize interface for Consensus (and all other components)
    @property
    def consensus_id(self):
        return self.consensus.joining_id

    # TODO Formalize interface for PTM (and all other components)
    @property
    def ptm_peers(self):
        return self.private_manager.ptm_peers

    @property
    def ptm_url(self):
        return self.private_manager.ptm_url

    @property
    def ptm_address(self):
        return self.private_manager.ptm_address
