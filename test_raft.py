import raft
import random
import json
from utils.utils import make_param

# ---------------------- Test: Non defaults
print("==== START RAFT TEST ====")

test_d = {
    'context': "company1_q2_n0",
    'port': 5000,
    'block_time': 500,
    'peers': ["10.65.11.96"],
    'enode_id': "enode://b5790239b648470dfd3b01227f0cfef145b1633a4d11fd3f2ac5f15d0f92d58a311955ab0c6b81f215b9e0fbd19ea045143404\
6b4a7e58c26c74958e68443f8c@172.13.0.2:30303?discport=0",
    'node_state': 'initial'
}

print("Testing raft non default parameters...")
r = raft.Raft(test_d['context'],
              test_d['enode_id'],
              test_d['node_state'],
              test_d['port'],
              test_d['block_time'],
              test_d['peers']
              )

# Check if raft id properly written
build_configuration = r.build_configuration
raft_file = build_configuration['local']['raft_id_file']

print("For initial node, no raft id should be writtent to file. Checking this in {0}.".format(raft_file))
with open(raft_file, "r") as fp:
    raft_id = json.loads(fp.read())['raft_id']

    if raft_id is not None:
        raise Exception("Error: RAFT_ID for initial  network is not None ({0})."
                        .format(raft_id))


raft_launch_params = r.launch_parameters

print("Checking launch parameters")
if "raft" not in raft_launch_params or raft_launch_params["raft"] != "--raft":
    print(raft_launch_params)
    raise Exception("--raft flag error")

if "rpcapi" not in raft_launch_params or raft_launch_params["rpcapi"] != "--rpcapi raft":
    print(raft_launch_params)
    raise Exception("--rpcapi error")

if "raftport" not in raft_launch_params or raft_launch_params["raftport"] != make_param("--raftport", test_d['port']):
    print(raft_launch_params)
    raise Exception("--raftport error")

if "raftblocktime" not in raft_launch_params or raft_launch_params["raftblocktime"] != make_param("--raftblocktime", test_d['block_time']):
    print(raft_launch_params)
    raise Exception("--raftblocktime error")

if "raftjoinexisting" in raft_launch_params:
    print(raft_launch_params)
    raise Exception("--raftjoinexisting error")

if build_configuration['network']['peers'] != test_d['peers']:
    print(raft_launch_params)
    raise Exception("Peers expected {0} and actual {1} dont tally".
                    format(test_d['peers'], build_configuration['peers']))

# ---------------------- Test: Defaults
test_d = {
    'context': "company1_q2_n0",
    'enode_id': "enode://b5790239b648470dfd3b01227f0cfef145b1633a4d11fd3f2ac5f15d0f92d58a311955ab0c6b81f215b9e0fbd19ea045143404\
6b4a7e58c26c74958e68443f8c@172.13.0.2:30303?discport=0",
    'node_state': 'initial'
}

print("Testing raft default parameters...")
r = raft.Raft(test_d['context'],
              test_d['enode_id'],
              test_d['node_state']
              )

# Check if raft id properly written
build_configuration = r.build_configuration
raft_file = build_configuration['local']['raft_id_file']

print("For initial node, no raft id should be written to file. Checking this in {0}.".format(raft_file))
with open(raft_file, "r") as fp:
    raft_id = json.loads(fp.read())['raft_id']

    if raft_id is not None:
        raise Exception("Error: RAFT_ID for initial  network is not None ({0})."
                        .format(raft_id))


raft_launch_params = r.launch_parameters
print("Checking launch parameters")

if "raft" not in raft_launch_params or raft_launch_params["raft"] != "--raft":
    print(raft_launch_params)
    raise Exception("--raft flag error")

if "rpcapi" not in raft_launch_params or raft_launch_params["rpcapi"] != make_param("--rpcapi", "raft"):
    print(raft_launch_params)
    raise Exception("--rpcapi error")

if "raftport" not in raft_launch_params or raft_launch_params["raftport"] != make_param("--raftport", 50400):
    print(raft_launch_params)
    raise Exception("--raftport error")

if "raftblocktime" not in raft_launch_params or raft_launch_params["raftblocktime"] != make_param("--raftblocktime", 50):
    print(raft_launch_params)
    raise Exception("--raftblocktime error")

if "raftjoinexisting" in raft_launch_params:
    print(raft_launch_params)
    raise Exception("--raftjoinexisting error")

if build_configuration['network']['peers'] != []:
    print(raft_launch_params)
    raise Exception("Peers expected {0} and actual {1} dont tally".
                    format([], build_configuration['network']['peers']))

print("==== PASS ====")





