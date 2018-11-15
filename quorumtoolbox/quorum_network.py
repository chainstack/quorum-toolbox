import json
import os
import pathlib

from quorumtoolbox.quorum_node import QuorumNode
from quorumtoolbox.utils import fs_utils, templating


class QuorumNetwork:
    blockchain_dir_name = 'blockchain'
    qdata_dir_name = 'qdata'
    dd_dir_name = 'dd'

    static_nodes_file_name = 'static-nodes.json'
    genesis_file_name = 'genesis.json'

    genesis_template_file_name = str(pathlib.Path(__file__).parent / pathlib.Path('genesis_template'))

    def __init__(self,
                 no_of_nodes,
                 networkid,
                 contexts,
                 addresses,
                 rpcaddrs,
                 node_state,
                 genesis_content='',
                 geth_params={},
                 consensus_params={},
                 private_manager_params={}):
        self.genesis_template_file = self.genesis_template_file_name

        self.no_of_nodes = no_of_nodes
        self._networkid = networkid
        self.node_state = node_state
        self.quorum_nodes = []
        self.genesis_content = genesis_content  # genesis content will be filled/created to genesis.json of all nodes
        self.base_dirs = []
        self.dd_dirs = []
        self.static_nodes_files = []
        self.genesis_files = []

        self.enode_ids = []
        self._accounts = []
        self.consensus_ids = []
        self.private_manager_peers = []
        self.private_manager_urls = []

        if self.node_state == 'new' and self.genesis_content == '':  # genesis content will be created for initial
            raise Exception('New nodes of network require genesis content which is empty')

        for context, address, rpcaddr in zip(contexts, addresses, rpcaddrs):
            base_dir = os.path.join(context, self.blockchain_dir_name)
            dd_dir = os.path.join(base_dir, self.qdata_dir_name, self.dd_dir_name)
            static_nodes_file = os.path.join(dd_dir, self.static_nodes_file_name)
            genesis_file = os.path.join(base_dir, self.genesis_file_name)

            self.base_dirs.append(base_dir)
            self.dd_dirs.append(dd_dir)
            self.static_nodes_files.append(static_nodes_file)
            self.genesis_files.append(genesis_file)

            self.make_quorum_node(networkid,
                                  context,
                                  address,
                                  rpcaddr,
                                  node_state,
                                  geth_params,
                                  consensus_params,
                                  private_manager_params
                                  )

        if self.node_state == 'initial':  # static-nodes.json for initial network only.
            self.write_static_nodes()

        self.write_genesis()

        self.build_config = {
            'local': {
                'static_nodes_files': self.static_nodes_files if self.node_state == 'initial' else [],
                'genesis_files': self.genesis_files
            },

            'network': {
                'networkid': self._networkid,
                'no_of_nodes': self.no_of_nodes,
                'enode_ids': self.enode_ids,
                'genesis': json.loads(self.genesis_content),
                'accounts': self._accounts,
                'consensus_ids': self.consensus_ids,
                'private_manager_peers': self.private_manager_peers,
                'private_manager_urls': self.private_manager_urls
            }
        }

    def make_quorum_node(self,
                         networkid,
                         context,
                         address,
                         rpcaddr,
                         node_state,
                         geth_params,
                         consensus_params,
                         private_manager_params):
        quorum_node = QuorumNode(context,
                                 address,
                                 rpcaddr,
                                 networkid,
                                 node_state,
                                 geth_params=geth_params,
                                 consensus_params=consensus_params,
                                 private_manager_params=private_manager_params)
        self.quorum_nodes.append(quorum_node)
        # can be appended? See write_geneis also.
        self._accounts.extend(quorum_node.accounts)
        self.enode_ids.append(quorum_node.enode_id)
        self.consensus_ids.append(quorum_node.consensus_id)
        self.private_manager_peers.append(quorum_node.ptm_peers)
        self.private_manager_urls.append(quorum_node.ptm_url)

    def write_static_nodes(self):
        for static_nodes_file in self.static_nodes_files:
            fs_utils.write_file(static_nodes_file, json.dumps(self.enode_ids))

    def write_genesis(self):
        if self.node_state == 'initial':
            # Create genesis content for initial nodes
            account_balances = {}
            for account in self._accounts:
                account_balances[account] = {
                    'balance': '1000000000000000000000000000'
                }

            self.genesis_content = templating.template_substitute(self.genesis_template_file,
                                                                  {
                                                                      'account_balances': json.dumps(account_balances),
                                                                      'chain_id': self._networkid
                                                                  },
                                                                  write=False)
        self.write_genesis_file()

    def write_genesis_file(self):
        for genesis_file in self.genesis_files:
            fs_utils.write_file(genesis_file, self.genesis_content)

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def networkid(self):
        return self._networkid

    @property
    def accounts(self):
        return self._accounts
