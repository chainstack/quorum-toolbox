import json
import os
import re

from quorumtoolbox.geth import Geth
from quorumtoolbox.utils import make_param


def check_accounts(geth_i, no_of_accounts):
    keystore_dir = geth_i.build_configuration['local']['keystore_dir']

    count = 0
    found = 0
    for root, dirs, files in os.walk(keystore_dir):
        for filename in files:
            if "UTC" in filename:
                count += 1

            with open(os.path.join(root, filename), "r") as fp:
                try:
                    account_json = json.loads(fp.read())
                    if account_json['address'] == geth_i.accounts[0]:
                        found += 1
                except Exception:
                    continue

            print("Deleting account key file {0} as part of test.".format(os.path.join(root, filename)))
            os.remove(os.path.join(root, filename))

    if count != no_of_accounts:
        raise Exception("Expected one account file, found {0}".format(count))

    if found == 0:
        raise Exception("Unable to find account {0} in keystore file.".format(geth_i.accounts[0]))

    if found != no_of_accounts:
        raise Exception(
            "Expected account {0} to be in one file only, found in multiple files.".format(geth_i.accounts[0]))

    if no_of_accounts != geth_i.no_of_accounts:
        raise Exception("Expected {0} number of accounts, got {1}.".format(no_of_accounts, geth_i.no_of_accounts))


# ---------------------- Test: Non defaults
print("==== START GETH TEST ====")

test_param = {
    'context': "company1_q2_n0",
    'addr': "127.0.0.1",
    'rpcaddr': '10.65.11.96',
    'network_id': 1981,
    'port': 5000,
    'rpcport': 9999,
    'max_peers': 100
}

print("Testing geth non default parameters...")
geth = Geth(test_param['context'],
            test_param['addr'],
            test_param['rpcaddr'],
            test_param['network_id'],
            port=test_param['port'],
            rpcport=test_param['rpcport'],
            max_peers=test_param['max_peers'])

print("Checking nodekey ...")
build_config = geth.build_config

nodekey_file = build_config['local']['nodekey_file']
with open(nodekey_file, "r") as fp:
    nodekey = fp.read()
    if len(nodekey) != 64:
        raise Exception("Generated nodekey {0} in file {1} is of incorrect length {2}, expected {3}"
                        .format(nodekey, nodekey_file, len(nodekey), 64))

print("Checking enode and enode_id_geth")
enode = build_config['network']['enode']
enode_id_geth = build_config['network']['enode_id_geth']

if len(enode) != 128:
    raise Exception("Generated enode {0} is of incorrect length {1}, expected {2}".format(enode, len(enode), 128))

# "enode://35cf975685f7aae0a6a70c80f536e6259e2898e23fcd5b3752924dec50c88b9d6b7e7c889632f37e2af3589cdd4f4c2e8081e3869f4024\
# a7cf7370aecab58d74@172.13.0.2:30303"
r = re.compile("^enode://([a-zA-Z0-9]{128,128})@([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}):([0-9]+)")
o = r.search(enode_id_geth)

if not o:
    raise Exception("Improper format of enode_id_geth {0}".format(enode_id_geth))

if o.group(1) != enode:
    raise Exception("Enode {0} not found in enode_id_geth {1}".format(enode, enode_id_geth))

if o.group(2) != test_param['addr']:
    raise Exception("Unable to find address {0} in enode_id_geth {1}".format(test_param['addr'], enode_id_geth))

if o.group(3) != str(test_param['port']):
    raise Exception("Unable to find port {0} in {1} of enode_id_geth {2}".
                    format(test_param['port'], o.group(3), enode_id_geth))

print("Checking launch params....")
launch_params = geth.launch_params

if launch_params['rpcport'] != make_param("--rpcport", test_param['rpcport']):
    raise Exception("--rpcport is wrong in launch params {0}, expected {1}".format(launch_params, test_param['rpcport']))

if "maxpeers" not in launch_params or launch_params["maxpeers"] != make_param("--maxpeers", test_param['max_peers']):
    print(launch_params)
    raise Exception("--maxpeers error")

if geth.no_of_accounts != 1:
    raise Exception("Expected 1 account, got {0} accounts".format(geth.no_of_accounts))

check_accounts(geth, 1)
# ---------------------- Test: defaults
print("Testing geth default parameters...")
geth = Geth(test_param['context'],
            test_param['addr'],
            test_param['rpcaddr'],
            test_param['network_id'])

print("Checking nodekey ...")
build_config = geth.build_config

nodekey_file = build_config['local']['nodekey_file']
with open(nodekey_file, "r") as fp:
    nodekey = fp.read()
    if len(nodekey) != 64:
        raise Exception("Generated nodekey {0} is of incorrect length {1}, expected {2}".format(nodekey, len(nodekey), 64))

print("Checking enode and enode_id_geth")
enode = build_config['network']['enode']
enode_id_geth = build_config['network']['enode_id_geth']

if len(enode) != 128:
    raise Exception("Generated enode {0} is of incorrect length {1}, expected {2}".format(enode, len(enode), 128))

# "enode://35cf975685f7aae0a6a70c80f536e6259e2898e23fcd5b3752924dec50c88b9d6b7e7c889632f37e2af3589cdd4f4c2e8081e3869f4024\
# a7cf7370aecab58d74@172.13.0.2:30303"
r = re.compile("^enode://([a-zA-Z0-9]{128,128})@([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}):([0-9]+)")
o = r.search(enode_id_geth)

if not o:
    raise Exception("Improper format of enode_id_geth {0}".format(enode_id_geth))

if o.group(1) != enode:
    raise Exception("Enode {0} not found in enode_id_geth {1}".format(enode, enode_id_geth))

if o.group(2) != test_param['addr']:
    raise Exception("Unable to find address {0} in enode_id_geth {1}".format(test_param['addr'], enode_id_geth))

if o.group(3) != "30303":
    raise Exception("Default port 30303 not in enode_id_geth {0}".format(enode_id_geth))

print("Checking launch params....")
launch_params = geth.launch_params

if launch_params['rpcport'] != make_param("--rpcport", 8545):
    raise Exception("--rpcport is wrong in launch params {0}, expected {1}".format(launch_params, 8545))

if "maxpeers" not in launch_params or launch_params["maxpeers"] != make_param("--maxpeers", 25):
    print(launch_params)
    raise Exception("--maxpeers error")

check_accounts(geth, 1)
# ---------------------------------------------------------------------------------
print("==== PASS ====")
