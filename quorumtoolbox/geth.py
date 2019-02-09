import os

from quorumtoolbox.utils import bash_utils, enode_utils
from quorumtoolbox.utils.node_utils import make_node_param


class Geth:
    blockchain_dir_name = 'blockchain'
    qdata_dir_name = 'qdata'
    dd_dir_name = 'dd'
    keystore_dir_name = 'keystore'
    geth_dir_name = 'geth'
    chaindata_dir_name = 'chaindata'
    logs_dir_name = 'logs'

    nodekey_file_name = 'nodekey'
    socket_file_name = 'geth.ipc'
    log_file_name = 'geth.log'
    passwords_file_name = 'passwords.txt'

    def __init__(self,
                 context,
                 address,
                 rpcaddr,  # default rpcaddr is localhost. So, explicitly ask for it.
                 networkid,
                 port=30303,  # default in Quorum. needed to make enode_id_geth.
                 rpcport=8545,  # default in Quorum.
                 max_peers=25):  # default in Quorum
        self.base_dir = os.path.join(context, self.blockchain_dir_name)
        self.qdata_dir = os.path.join(self.base_dir, self.qdata_dir_name)
        self.dd_dir = os.path.join(self.qdata_dir, self.dd_dir_name)
        self.keystore_dir = os.path.join(self.dd_dir, self.keystore_dir_name)
        self.geth_dir = os.path.join(self.dd_dir, self.geth_dir_name)
        self.chaindata_dir = os.path.join(self.geth_dir, self.chaindata_dir_name)
        self.logs_dir = os.path.join(self.dd_dir, self.logs_dir_name)

        self.nodekey_file = os.path.join(self.geth_dir, self.nodekey_file_name)
        self.socket_file = os.path.join(self.dd_dir, self.socket_file_name)
        self.log_file = os.path.join(self.logs_dir, self.log_file_name)
        self.passwords_file = os.path.join(self.base_dir, self.passwords_file_name)

        self.address = address
        self.port = port
        self.rpcport = rpcport
        self.max_peers = max_peers

        # ibft address is generated from nodekey, and is generated always. It is up the caller to use it or not.
        self._ibft_address, self._nodekey, self.enode = self.generate_ibftaddress_nodekey_enode()

        self._enode_id_geth = self.make_enode_id_geth()

        self.rpcaddr = rpcaddr

        self.geth_accounts = []
        self.generate_new_account()  # only one account per node for now

        self.networkid = networkid

        self.build_config = {
            'network': {
                'address': self.address,
                'port': self.port,
                'enode': self.enode,
                'enode_id_geth': self.enode_id_geth,
                'ibft_address': self.ibft_address,
                'max_peers': self.max_peers
            },

            'local': {
                'ipc': self.socket_file,
                'log_file': self.log_file,
                'nodekey_file': self.nodekey_file,
                'keystore_dir': self.keystore_dir,
                'chaindata_dir': self.chaindata_dir
            },

            'keys': {
                'nodekey': self.nodekey
            }
        }

        # common geth launch parameters
        self.launch_params = {
            'geth_binary': 'geth',
            'datadir': make_node_param('--datadir', os.path.join(self.qdata_dir_name, self.dd_dir_name)),
            'maxpeers': make_node_param('--maxpeers', self.max_peers),  # max peers in network
            'geth_log_file': os.path.join(self.qdata_dir_name, self.dd_dir_name, self.logs_dir_name,
                                          self.log_file_name),
            'unlock': '--unlock 0',  # only one account for now. So unlock first account.
            'password': make_node_param('--password', self.passwords_file_name),
            'networkid': make_node_param('--networkid', self.networkid),
            'verbosity': make_node_param('--verbosity', 2),  # 5 is highest

            # RPC related
            'rpc': '--rpc',
            'rpcaddr': make_node_param('--rpcaddr', self.rpcaddr),
            'rpcport': make_node_param('--rpcport', self.rpcport),
            'rpcapi': make_node_param('--rpcapi', 'admin,db,eth,debug,miner,net,shh,txpool,personal,web3,'
                                                  'quorum'),
            'rpccorsdomain': '?',

            # network related
            'port': make_node_param('--port', self.port),
            'nodiscover': '--nodiscover',  # For private networks, all peer additions are manual.
            'permissioned': '?',
            'targetgaslimit': '?',

            # whisper related
            'shh': '?',

            # web sockets related
            'ws': '?',
            'wsaddr': '?',
            'wsport': '?',
            'wsapi': '?',
            'wsorigins': '?',

            # others
            'nat': '?',
            'web3': '?',
            'chaindatadir': os.path.join(self.qdata_dir_name,
                                         self.dd_dir_name,
                                         self.geth_dir_name,
                                         self.chaindata_dir_name)
        }

    def generate_new_account(self):
        self.accounts.append(bash_utils.generate_geth_account(self.dd_dir, self.passwords_file))

    @property
    def accounts(self):
        return self.geth_accounts

    @property
    def no_of_accounts(self):
        return len(self.geth_accounts)

    def generate_node_key(self):
        bash_utils.generate_nodekey(self.nodekey_file)

    def generate_enode(self):
        bash_utils.generate_enode(self.nodekey_file)

    def generate_ibftaddress_nodekey_enode(self):
        return bash_utils.generate_ibftaddress_nodekey_enode(self.nodekey_file)

    def generate_nodekey_and_enode(self):
        return bash_utils.generate_nodekey_and_enode(self.nodekey_file)

    def make_enode_id_geth(self):
        return enode_utils.make_enode_id_geth(self.enode, self.address, self.port)

    @property
    def launch_parameters(self):
        return self.launch_params

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def ibft_address(self):
        return self._ibft_address

    @property
    def enode_id_geth(self):
        return self._enode_id_geth

    @property
    def nodekey(self):
        return self._nodekey
