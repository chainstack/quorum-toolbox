import os

from quorumtoolbox.constellation import Constellation
from quorumtoolbox.geth import Geth
from quorumtoolbox.raft import Raft
from quorumtoolbox.utils import enode_utils, bash_utils


class QuorumNode:
    blockchain_dir_name = 'blockchain'
    quorum_node_config_file_name = 'quorum_node_config.sh'

    def __init__(self,
                 context,
                 address,
                 rpcaddr,
                 networkid,
                 node_state,
                 consensus='raft',
                 private_manager='constellation',
                 geth_params={},
                 consensus_params={},
                 private_manager_params={}):
        self.base_dir = os.path.join(context, self.blockchain_dir_name)
        self.quorum_node_config_file = os.path.join(self.base_dir, self.quorum_node_config_file_name)

        self.geth = Geth(context, address, rpcaddr, networkid, **geth_params)

        if consensus.lower() == 'raft':
            self.consensus = Raft(context, self.geth.enode_id_geth, node_state, **consensus_params)

        if private_manager.lower() == 'constellation':
            self.private_manager = Constellation(context, address, **private_manager_params)

        self._enode_id = enode_utils.make_enode_id2(self.geth.enode_id_geth,
                                                    self.consensus.build_configuration['network']['port'])

        self.launch_params = bash_utils.make_quorum_node_launch_params([self.geth.launch_parameters,
                                                                        self.consensus.launch_parameters,
                                                                        self.private_manager.launch_parameters
                                                                        ])  # get launch params from components, combine to launch this node

        bash_utils.write_quorum_node_launch_config(self.launch_params, self.quorum_node_config_file)

        self.build_config = {
            'local': {
                'config_file': self.quorum_node_config_file
            },

            'geth': self.geth.build_configuration,
            'consensus': self.consensus.build_configuration,
            'private_manager': self.private_manager.build_configuration
        }

    @property
    def launch_parameters(self):
        return self.launch_parameters

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def enode_id(self):
        return self._enode_id

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
