import os
import re

from quorumtoolbox.utils import bash_utils


def make_tessera_key(key_name, store_dir=""):
    key_name = os.path.join(store_dir, key_name)
    bash_utils.generate_tessera_key(key_name)


def read_tessera_key(key_name, store_dir=""):
    with open(os.path.join(store_dir, key_name), "r") as fp:
        return fp.read()


def make_url(address, port):
    r = re.compile(r'^https://')
    if r.match(address) is None:
        address = 'https://' + address

    if address[-1] == '/':
        address = address[:-1] + ':' + str(port)
    else:
        address = address + ':' + str(port)

    return address
