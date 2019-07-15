import os
import json

from utils import tessera_utils
from utils import templating


class Tessera:
    tessera_dir_name = "tessera"
    keys_dir_name = "keys"
    logs_dir_name = "logs"

    socket_file_name = "tessera.ipc"
    config_file_name = "tessera.config"

    key_name_pfx = "node"

    pub_key_file_name = key_name_pfx + ".pub"
    pri_key_file_name = key_name_pfx + ".key"

    def __init__(self,
                 context,
                 address,
                 port=9000,         # default in quorum. needed to make config file.
                 other_nodes=None):
        self.context = context
        self.address = address
        self.port = port

        other_nodes = [] if other_nodes is None else other_nodes
        self._other_nodes = [constellation_utils.make_url(node, 9000) for node in other_nodes]

        self.url = tessera_utils.make_url(self.address, self.port)

        self.base_dir = os.path.join(context, self.tessera_dir_name)
        self.keys_dir = os.path.join(self.base_dir, self.keys_dir_name)

        self.config_file = os.path.join(self.base_dir, self.config_file_name)
        self.socket_file = os.path.join(self.base_dir, self.socket_file_name)

        self.public_keys = []
        self.private_keys = []
        self.public_keys_contents = []
        self.private_keys_contents = []

        self.make_keys()
        self.public_keys.append(os.path.join(self.keys_dir, self.pub_key_file_name))
        self.private_keys.append(os.path.join(self.keys_dir, self.pri_key_file_name))

        for key_file in self.public_keys:
            self.public_keys_contents.append(tessera_utils.read_tessera_key(key_file))

        for key_file in self.private_keys:
            self.private_keys_contents.append(tessera_utils.read_tessera_key(key_file))

        # configuration related to this class instance
        self.build_config = {
            'network': {
                'url': self.url,
                'port': self.port,
                'othernodes': self._other_nodes
            },
            'local': {
                'ipc': self.socket_file,
            },
            'keys': {
                'public_keys': self.public_keys,
                'private_keys': self.private_keys,
                'public_keys_contents': self.public_keys_contents,
                'private_keys_contents': self.private_keys_contents
            }
        }

        # configuration related to launching this instance of tessera, goes into a config file.
        # to be launched from within the tessera_dir_name
        self.launch_config = {
            'url': self.url,
            'socket': self.socket_file_name,

            # relative to tessera_dir_name folder
            'publickeys': [os.path.join(self.keys_dir_name, self.pub_key_file_name)],

            # relative to tessera_dir_name folder
            'privatekeys': [os.path.join(self.keys_dir_name, self.pri_key_file_name)],
        }

        self.write_launch_configuration_file()

        self.launch_params = {
            'tessera_binary': 'tessera',
            'tessera_config_file': self.config_file_name,
            'tessera_ipc_file': self.socket_file_name,
            'othernodes': self._other_nodes,
        }

    @property
    def launch_parameters(self):
        return self.launch_params

    @property
    def launch_configuration(self):
        return self.launch_config

    @property
    def build_configuration(self):
        return self.build_config

    @property
    def ptm_peers(self):
        return self._other_nodes

    def write_launch_configuration_file(self):
        templating.template_substitute(self.config_file, self.launch_config)

    def make_keys(self):
        tessera_utils.make_tessera_key(self.key_name_pfx, self.keys_dir)

    def __str__(self):
        return json.dumps(self.build_config)
