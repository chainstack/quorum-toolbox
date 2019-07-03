import os
import re

from . import bash_utils


def make_tessera_key(key_name, store_dir=""):
    key_name = os.path.join(store_dir, key_name)
    result = bash_utils.generate_tessera_key(key_name)

    if result[0] != 0:
        raise Exception("Unable to make tessera keys: {0}, {1}".format(result[1], result[2]))


def read_tessera_key(key_name, store_dir=""):
    with open(os.path.join(store_dir, key_name), "r") as fp:
        return fp.read()

# Same?? TLS?
def make_url(address, port):
    r = re.compile("^http://")
    if r.match(address) is None:
        address = "http://" + address

    if address[-1] == "/":                                  # must end in /, if not error on launching constellation
        address = address[:-1] + ":" + str(port) + "/"
    else:
        address = address + ":" + str(port) + "/"

    return address






