import os

from quorumtoolbox.utils import bash_utils


def make_constellation_key(key_name, store_dir=''):
    key_name = os.path.join(store_dir, key_name)
    bash_utils.generate_constellation_key(key_name)


def read_constellation_key(key_name, store_dir=''):
    with open(os.path.join(store_dir, key_name), 'r') as fp:
        return fp.read()
