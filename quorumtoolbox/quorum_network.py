# coding=utf-8
import json
import os
import pathlib

from quorumtoolbox.quorum_node import QuorumNode
from quorumtoolbox.utils import fs_utils, templating, node_utils, bash_utils


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
                 private_manager='constellation',
                 genesis_content='',
                 geth_params=None,
                 consensus_params=None,
                 private_manager_params=None):

        self.no_of_nodes = no_of_nodes
        self._networkid = networkid
        self.node_state = node_state
        self.private_manager = private_manager
        self.quorum_nodes = []

        # genesis content will be (created and) written to genesis.json of all nodes
        self.genesis_content = genesis_content
        self.base_dirs = []
        self.dd_dirs = []
        self.static_nodes_files = []
        self.genesis_files = []
        self.genesis_template_file = ''

        self._enode_ids = []
        self._ibft_addresses = []  # ibft address is always returned by geth. Use it if ibft consensus is used.
        self._accounts = []
        self._consensus_ids = []
        self._private_manager_peers = []
        self._private_manager_urls = []
        self._private_manager_addresses = []

        geth_params = {} if geth_params is None else geth_params
        consensus_params = {} if consensus_params is None else consensus_params
        private_manager_params = {} if private_manager_params is None else private_manager_params

        self.is_raft_or_istanbul_node()  # raft or istanbul nodes are supported
        self.is_constellation_or_tessera_node()  # constellation or tessera ptms are supported
        self.set_genesis_template_filename()  # choose the right genesis file
        self.is_genesis_content_needed()  # genesis must be given for new nodes, will be created for initial nodes

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
                                  private_manager,
                                  geth_params,
                                  consensus_params,
                                  private_manager_params
                                  )

        # static-nodes.json for initial nodes only.
        if self.is_initial_node():
            self.write_static_nodes()

        self.write_genesis()

        self.build_config = {
            'local': {
                'static_nodes_files': self.static_nodes_files if self.is_initial_node() else [],
                'genesis_files': self.genesis_files
            },

            'network': {
                'networkid': self._networkid,
                'no_of_nodes': self.no_of_nodes,
                'enode_ids': self._enode_ids,
                'genesis': json.loads(self.genesis_content),
                'accounts': self._accounts,
                'ibft_addresses': self._ibft_addresses,
                'consensus_ids': self._consensus_ids,
                'private_manager_peers': self._private_manager_peers,
                'private_manager_urls': self._private_manager_urls,
                'private_manager_addresses': self._private_manager_addresses
            }
        }

    def is_genesis_content_needed(self):
        if self.is_new_node() and not self.genesis_content:
            raise Exception('New nodes of network require genesis content to be given. But what is given is empty.')

    def is_istanbul_node(self):
        return node_utils.is_istanbul_node(self.node_state)

    def is_raft_node(self):
        return node_utils.is_raft_node(self.node_state)

    def is_raft_or_istanbul_node(self):
        if node_utils.is_raft_or_istanbul_node(self.node_state):
            return True
        else:
            raise Exception('Unknown node type: {0}'.format(self.node_state))

    def is_constellation_or_tessera_node(self):
        if node_utils.is_constellation_or_tessera_node(self.private_manager):
            return True
        else:
            raise Exception('Unknown ptm type: {0}'.format(self.private_manager))

    def is_initial_node(self):
        return node_utils.is_initial_node(self.node_state)

    def is_new_node(self):
        return node_utils.is_new_node(self.node_state)

    def set_genesis_template_filename(self):
        self.genesis_template_file = self.genesis_template_file_name  # raft

        if self.is_istanbul_node():
            self.genesis_template_file = self.genesis_template_file_name + '_ibft'  # ibft

    def make_quorum_node(self,
                         networkid,
                         context,
                         address,
                         rpcaddr,
                         node_state,
                         private_manager,
                         geth_params,
                         consensus_params,
                         private_manager_params):
        quorum_node = QuorumNode(context,
                                 address,
                                 rpcaddr,
                                 networkid,
                                 node_state,
                                 private_manager=private_manager,
                                 geth_params=geth_params,
                                 consensus_params=consensus_params,
                                 private_manager_params=private_manager_params)
        self.quorum_nodes.append(quorum_node)
        self._accounts.extend(quorum_node.accounts)
        self._enode_ids.append(quorum_node.enode_id)
        self._ibft_addresses.append(quorum_node.ibft_address)
        self._consensus_ids.append(quorum_node.consensus_id)
        self._private_manager_peers.append(quorum_node.ptm_peers)
        self._private_manager_urls.append(quorum_node.ptm_url)
        self._private_manager_addresses.append(quorum_node.ptm_address)

    def write_static_nodes(self):
        for static_nodes_file in self.static_nodes_files:
            fs_utils.write_file(static_nodes_file, json.dumps(self.enode_ids))

    def write_genesis(self):
        if self.is_initial_node():  # create genesis content for initial nodes only
            account_balances = self.prefund_accounts()  # pre-fund each account of the nodes
            extra_data = self.create_extra_data()  # create extra_data for raft or ibft

            self.genesis_content = templating.template_substitute(
                self.genesis_template_file,
                {
                    'account_balances': json.dumps(account_balances),
                    'chain_id': self._networkid,
                    'extra_data': json.dumps(extra_data)
                },
                write=False)

        self.write_genesis_file()

    def prefund_accounts(self):
        account_balances = {}
        for account in self._accounts:
            account_balances[account] = {
                'balance': '1000000000000000000000000000'
            }

        return account_balances

    def create_extra_data(self):
        if self.is_raft_node():
            return self.create_raft_extra_data()
        else:
            return self.create_ibft_extra_data()

    @staticmethod
    def create_raft_extra_data():
        # dummy for raft
        return '0x0000000000000000000000000000000000000000000000000000000000000000'

    def create_ibft_extra_data(self):
        return bash_utils.generate_ibft_extradata(self.ibft_addresses)

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

    @property
    def ibft_addresses(self):
        return self._ibft_addresses

    @property
    def consensus_ids(self):
        return self._consensus_ids

    @property
    def enode_ids(self):
        return self._enode_ids

    @property
    def private_manager_peers(self):
        return self._private_manager_peers

    @property
    def private_manager_urls(self):
        return self._private_manager_urls

    @property
    def private_manager_addresses(self):
        return self._private_manager_addresses
