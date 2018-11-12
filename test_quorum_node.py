import re

from quorum_node import QuorumNode


# ------------------ Test Raft, Constellation and Geth --------------------------------

constellation_params = {
    'other_nodes': ["http://127.0.0.1:9000/", "http://10.11.11.11:9000/"]
}

raft_params = {

}

geth_params = {
    'max_peers': 200
}

node_options = {
    'context': "company1_q2_n0",
    'address': "10.65.11.96",
    'rpcaddr': "10.65.11.96",
    'network_id': 1981,
    'node_state': "initial",
    'consensus': "raft",
    'consensus_params': raft_params,
    'private_manager': "constellation",
    'private_manager_params': constellation_params,
    'geth_params': geth_params
}

print("==== START QUORUM NODE TEST ====")

print("Creating a Quorum node with consensus: {0} and private manager: {1}"
      .format(node_options['consensus'],
              node_options['private_manager']))

qn = QuorumNode(node_options['context'],
                node_options['address'],
                node_options['rpcaddr'],
                node_options['network_id'],
                node_options['node_state'],
                consensus=node_options['consensus'],
                private_manager=node_options['private_manager'],
                geth_params=node_options['geth_params'],
                consensus_params=node_options['consensus_params'],
                private_manager_params=node_options['private_manager_params'])

print("Checking accounts...")
if len(qn.accounts) != 1:
    print("Expected 1 account, but found {0}".format(len(qn.accounts)))
print("Accounts: ", qn.accounts)

print("Checking enode_id...")
regex = re.compile("^enode://[\d\w]{128}@\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d+\?discport=0&raftport=\d+")
result = regex.match(qn.enode_id)

if not result:
    raise Exception("Enode id is of wrong format {0}".format(qn.enode_id))
print("Enode id: ", qn.enode_id)

config_file = qn.build_configuration['local']['config_file']


def config_check(fullstr):
    def closure_check(substr):
        regex = re.compile(substr, re.MULTILINE)        # multiline so ^/$ matches at starting/ending of new line also.
        result = regex.search(fullstr)
        if result is None:
            raise Exception("{0} not found in config file {1}".format(substr, config_file))

    return closure_check


def config_check_if_present(fullstr):
    def closure_check_if_present(flag, substr):
        regex = re.compile(flag, re.MULTILINE)
        result = regex.search(fullstr)
        if result is not None:
            check1 = config_check(fullstr)
            check1(substr)


print("Checking node config file {0}".format(config_file))

with open(config_file, "r") as fp:
    config = fp.read()
    check = config_check(config)

    # compulsory
    check('^DATADIR=\"--datadir qdata/dd\"$')
    check('^NODISCOVER=\"--nodiscover\"$')
    check('^NETWORKID=\"--networkid \d+\"$')

    check('^PORT=\"--port \d+\"$')
    check('^RPC=\"--rpc\"$')

    check('^RPCADDR=\"--rpcaddr \S+\"$')

    check('^RPCPORT=\"--rpcport \d+\"$')
    check('^RPCAPI=\"--rpcapi \S+\"$')      # \S any non white space char
    check('^VERBOSITY=\"--verbosity \d\"$')

    check('^RAFT=\"--raft\"$')
    check('^RAFTPORT=\"--raftport \d+\"$')
    check('^MAXPEERS=\"--maxpeers \d+\"$')
    check('^RAFTBLOCKTIME=\"--raftblocktime \d+\"$')

    check('^GETH_BINARY=\"geth\"$')
    check('^CONSTELLATION_BINARY=\"constellation-node\"$')

    check('^CHAINDATADIR=\"qdata/dd/geth/chaindata\"$')
    check('^CONSTELLATION_CONFIG_FILE=\"constellation.config\"$')
    check('^CONSTELLATION_LOG_FILE=\"logs/constellation.log\"$')
    check('^CONSTELLATION_IPC_FILE=\"constellation.ipc\"$')

    check('^GETH_LOG_FILE=\"qdata/dd/logs/geth.log\"$')

    ls = config.split("\n")
    for line in ls:
        if "RPCADDR" in line:
            ip_ls = line.replace("\"", "").split("--rpcaddr ")[1].split(".")
            if len(ip_ls) != 4:
                raise Exception("--rpcaddr ip wrong format {0}".format(ip_ls))
            for elem in ip_ls:
                if int(elem) > 255 or int(elem) < 0:
                    raise Exception("--rpcaddr ip wrong format {0}".format(ip_ls))

"""
check('^CONSTELLATION_IPC_FILE_DIR=$')

check('^EMITCHECKPOINTS=\"--emitcheckpoints\"$') # istanbul

$RAFTJOINEXISTING
$RPCCORSDOMIAN $UNLOCK $PASSWORD
$TARGETGASLIMIT

$SHH $WS $WSADDR $WSPORT $WSAPI $WSORIGINS $NAT
"""
print("==== PASS ====")