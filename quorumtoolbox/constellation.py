import json
import os

from quorumtoolbox.utils import constellation_utils, templating
from quorumtoolbox.utils.bash_utils import launch_constellation


class Constellation:
    constellation_dir_name = 'constellation'
    storage_dir_name = 'storage'
    keys_dir_name = 'keys'
    logs_dir_name = 'logs'

    socket_file_name = 'constellation.ipc'
    config_file_name = 'constellation.config'
    log_file_name = 'constellation.log'
    launch_script_file_name = 'launch_constellation.sh'

    key_name_pfx = 'node'

    pub_key_file_name = key_name_pfx + '.pub'
    pri_key_file_name = key_name_pfx + '.key'

    def __init__(self,
                 context,
                 address,
                 port=9000,  # default in quorum. needed to make config file.
                 other_nodes=None):
        self.context = context
        self.address = address
        self.port = port

        other_nodes = [] if other_nodes is None else other_nodes
        self._other_nodes = ''  # moved to orchestrator

        self._url = ''  # moved to orchestrator

        self.base_dir = os.path.join(context, self.constellation_dir_name)
        self.storage_dir = os.path.join(self.base_dir, self.storage_dir_name)
        self.keys_dir = os.path.join(self.base_dir, self.keys_dir_name)

        self.config_file = os.path.join(self.base_dir, self.config_file_name)
        self.socket_file = os.path.join(self.base_dir, self.socket_file_name)
        self.log_file = os.path.join(self.base_dir, self.logs_dir_name, self.log_file_name)

        self.launch_script_file = os.path.join(self.base_dir, self.launch_script_file_name)

        self.make_keys()

        self.public_key = os.path.join(self.keys_dir, self.pub_key_file_name)
        self.private_key = os.path.join(self.keys_dir, self.pri_key_file_name)
        self.public_key_content = constellation_utils.read_constellation_key(self.public_key)
        self.private_key_content = constellation_utils.read_constellation_key(self.private_key)

        self._ptm_address = self.public_key_content

        # configuration related to this class instance
        self.build_config = {
            'network': {
                'url': self._url,
                'port': self.port,
                'othernodes': self._other_nodes
            },
            'local': {
                'ipc': self.socket_file,
                'log_file': self.log_file,
                'storage_dir': self.storage_dir
            },
            'keys': {
                'public_key': self.public_key,
                'private_key': self.private_key,
                'public_key_content': self.public_key_content,
                'private_key_content': self.private_key_content
            }
        }

        # configuration related to launching this instance of constellation, goes into a config file.
        # to be launched from within the constellation_dir_name
        self.launch_config = {
            'url': self._url,
            'port': self.port,
            'socket': self.socket_file_name,
            'othernodes': self._other_nodes,

            # relative to constellation_dir_name folder
            'publickeys': [os.path.join(self.keys_dir_name, self.pub_key_file_name)],
            # relative to constellation_dir_name folder
            'privatekeys': [os.path.join(self.keys_dir_name, self.pri_key_file_name)],

            'storage': self.storage_dir_name
        }

        # to launch constellation binary via cmd line. To be launched from within the constellation_dir_name.
        self.launch_params = {
            # relative to constellation_dir_name folder
            'constellation_binary': 'constellation-node',
            'constellation_config_file': self.config_file_name,
            'constellation_log_file': os.path.join(self.logs_dir_name, self.log_file_name),
            'constellation_ipc_file': self.socket_file_name

        }

        # to be launched from within the constellation_dir_name. e.g nohup $binary $config_file_name 2>> $log_file
        self.launch_cmd_line = templating.template_substitute(
            '$constellation_binary $constellation_config_file 2>> $constellation_log_file',
            self.launch_params
        )

        self.write_launch_configuration_file()
        self.write_launch_script()

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
    def cmd_line_to_launch(self):
        return self.launch_cmd_line

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
        templating.template_substitute(self.config_file, self.launch_config)

    def write_launch_script(self):
        templating.template_substitute(self.launch_script_file, self.launch_params)

    def launch(self):
        launch_constellation(self.config_file_name,  # w.r.t to base_dir
                             self.log_file,  # w.r.t to curr dir since this is processed by sh
                             self.base_dir,  # cwd of script to be launched
                             self.port)

    def run_launch_script(self):
        pass

    def make_keys(self):
        constellation_utils.make_constellation_key(self.key_name_pfx, self.keys_dir)

    def get_ext_ip(self):
        pass

    def sanity_check(self):
        pass

    def __str__(self):
        return json.dumps(self.build_config)

    def __repr__(self):
        pass
