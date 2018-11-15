import os
import re

from quorumtoolbox.utils import bash_utils


def make_constellation_key(key_name, store_dir=""):
    key_name = os.path.join(store_dir, key_name)
    bash_utils.generate_constellation_key(key_name)


def read_constellation_key(key_name, store_dir=""):
    with open(os.path.join(store_dir, key_name), "r") as fp:
        return fp.read()


def make_url(address, port):
    r = re.compile("^https://")
    if r.match(address) is None:
        address = "https://" + address

    if address[-1] == "/":  # must end in /, if not error on launching constellation
        address = address[:-1] + ":" + str(port) + "/"
    else:
        address = address + ":" + str(port) + "/"

    return address
