import os
import json

from quorumtoolbox.utils import tessera_utils, templating


class Tessera:
    tessera_dir_name = "tessera"
    keys_dir_name = "keys"

    json_file_name = "tessera.json"

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
        self._other_nodes = [tessera_utils.make_url(node, 9000) for node in other_nodes]

        self._url = tessera_utils.make_url(self.address, self.port)

        self.base_dir = os.path.join(context, self.tessera_dir_name)
        self.keys_dir = os.path.join(self.base_dir, self.keys_dir_name)

        self.json_file = os.path.join(self.base_dir, self.json_file_name)

        self.public_keys = []
        self.private_keys = []
        self.public_keys_contents = []
        self.private_keys_contents = []

        self.make_keys()

        self.public_key = os.path.join(self.keys_dir, self.pub_key_file_name)
        self.private_key = os.path.join(self.keys_dir, self.pri_key_file_name)
        self.public_key_content = tessera_utils.read_tessera_key(self.public_key)
        self.private_key_content = tessera_utils.read_tessera_key(self.private_key)

        self._ptm_address = self.public_key_content

        # configuration related to this class instance
        self.build_config = {
            'network': {
                'url': self._url,
                'port': self.port,
                'othernodes': self._other_nodes
            },
            'keys': {
                'public_key': self.public_key,
                'private_key': self.private_key,
                'public_key_content': self.public_key_content,
                'private_key_content': self.private_key_content
            }
        }

        # configuration related to launching this instance of tessera, goes into a config file.
        # to be launched from within the tessera_dir_name
        self.launch_config = {
            'url': self._url,

            # relative to tessera_dir_name folder
            'publickeys': os.path.join(self.keys_dir_name, self.pub_key_file_name),

            # relative to tessera_dir_name folder
            'privatekeys': os.path.join(self.keys_dir_name, self.pri_key_file_name),
        }

        self.write_launch_configuration_file()

        self.launch_params = {
            'tessera_binary': 'tessera',
            'tessera_json_file': self.json_file_name,
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

    @property
    def ptm_url(self):
        return self._url

    @property
    def ptm_address(self):
        return self._ptm_address

    def write_launch_configuration_file(self):
        templating.template_substitute(self.json_file, self.launch_config)

    def make_keys(self):
        tessera_utils.make_tessera_key(self.key_name_pfx, self.keys_dir)

    def __str__(self):
        return json.dumps(self.build_config)
