import re
import sys

from quorumtoolbox.quorum_node import QuorumNode


def config_check(fullstr, config_file):
    def closure_check(substr):
        regex = re.compile(substr, re.MULTILINE)  # multiline so ^/$ matches at starting/ending of new line also.
        result = regex.search(fullstr)
        if result is None:
            raise Exception('{0} not found in config file {1}'.format(substr, config_file))

    return closure_check


constellation_params = {
    'other_nodes': ['http://127.0.0.1:9000/', 'http://10.11.11.11:9000/']
}

geth_params = {
    'max_peers': 200
}


# ------------------ Test Raft, Constellation and Geth --------------------------------


def test_raft_quorum_node():
    raft_params = {

    }

    node_options = {
        'context': 'company1_q2_n0',
        'address': '10.65.11.96',
        'rpcaddr': '10.65.11.96',
        'network_id': 1981,
        'node_state': 'initial',
        'consensus_params': raft_params,
        'private_manager': 'constellation',
        'private_manager_params': constellation_params,
        'geth_params': geth_params
    }

    print('==== START RAFT QUORUM NODE TEST ====')

    print('Creating a Quorum node with consensus: {0} and private manager: {1}'
          .format('RAFT',
                  node_options['private_manager']))

    qn = QuorumNode(node_options['context'],
                    node_options['address'],
                    node_options['rpcaddr'],
                    node_options['network_id'],
                    node_options['node_state'],
                    private_manager=node_options['private_manager'],
                    geth_params=node_options['geth_params'],
                    consensus_params=node_options['consensus_params'],
                    private_manager_params=node_options['private_manager_params'])

    print('Checking accounts...')
    if len(qn.accounts) != 1:
        print('Expected 1 account, but found {0}'.format(len(qn.accounts)))
    print('Accounts: ', qn.accounts)

    print('Checking enode_id...')
    regex = re.compile(r'^enode://[\d\w]{128}@\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d+\?discport=0&raftport=\d+$')
    result = regex.match(qn.enode_id)

    if not result:
        raise Exception('Enode id is of wrong format {0}'.format(qn.enode_id))
    print('Enode id: ', qn.enode_id)

    config_file = qn.build_configuration['local']['config_file']

    print('Checking node config file {0}'.format(config_file))

    with open(config_file, 'r') as fp:
        config = fp.read()
        check = config_check(config, config_file)

        # compulsory
        check(r'^DATADIR=\"--datadir qdata/dd\"$')
        check(r'^NODISCOVER=\"--nodiscover\"$')
        check(r'^NETWORKID=\"--networkid \d+\"$')

        check(r'^PORT=\"--port \d+\"$')
        check(r'^RPC=\"--rpc\"$')

        check(r'^RPCADDR=\"--rpcaddr \S+\"$')

        check(r'^RPCPORT=\"--rpcport \d+\"$')
        check(r'^RPCAPI=\"--rpcapi \S+\"$')  # \S any non white space char
        check(r'--rpcapi [\w\W]*raft')
        check(r'^VERBOSITY=\"--verbosity \d\"$')

        check(r'^RAFT=\"--raft\"$')
        check(r'^RAFTPORT=\"--raftport \d+\"$')
        check(r'^MAXPEERS=\"--maxpeers \d+\"$')
        check(r'^RAFTBLOCKTIME=\"--raftblocktime \d+\"$')

        check(r'^GETH_BINARY=\"geth\"$')
        check(r'^CONSTELLATION_BINARY=\"constellation-node\"$')

        check(r'^CHAINDATADIR=\"qdata/dd/geth/chaindata\"$')
        check(r'^CONSTELLATION_CONFIG_FILE=\"constellation.config\"$')
        check(r'^CONSTELLATION_LOG_FILE=\"logs/constellation.log\"$')
        check(r'^CONSTELLATION_IPC_FILE=\"constellation.ipc\"$')

        check(r'^GETH_LOG_FILE=\"qdata/dd/logs/geth.log\"$')

        ls = config.split('\n')
        for line in ls:
            if 'RPCADDR' in line:
                ip_ls = line.replace('"', '').split('--rpcaddr ')[1].split('.')
                if len(ip_ls) != 4:
                    raise Exception('--rpcaddr ip wrong format {0}'.format(ip_ls))
                for elem in ip_ls:
                    if int(elem) > 255 or int(elem) < 0:
                        raise Exception('--rpcaddr ip wrong format {0}'.format(ip_ls))

    print('==== PASS ====')


# ----------------------------------- Test Ibft, Constellation and Geth -------------------------------


def test_ibft_quorum_node():
    ibft_params = {

    }

    node_options = {
        'context': 'company1_q2_n0',
        'address': '10.65.11.96',
        'rpcaddr': '10.65.11.96',
        'network_id': 1981,
        'node_state': 'initial_ibft',
        'consensus_params': ibft_params,
        'private_manager': 'constellation',
        'private_manager_params': constellation_params,
        'geth_params': geth_params
    }

    print('==== START IBFT QUORUM NODE TEST ====')

    print('Creating a Quorum node with consensus: {0} and private manager: {1}'
          .format('IBFT',
                  node_options['private_manager']))

    qn = QuorumNode(node_options['context'],
                    node_options['address'],
                    node_options['rpcaddr'],
                    node_options['network_id'],
                    node_options['node_state'],
                    private_manager=node_options['private_manager'],
                    geth_params=node_options['geth_params'],
                    consensus_params=node_options['consensus_params'],
                    private_manager_params=node_options['private_manager_params'])

    # don't repeat account checking as its done during raft
    print('Checking enode_id...')
    regex = re.compile(r'^enode://[\d\w]{128}@\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d+\?discport=0$')
    result = regex.match(qn.enode_id)

    if not result:
        raise Exception('Enode id is of wrong format {0}'.format(qn.enode_id))
    print('Enode id: ', qn.enode_id)

    config_file = qn.build_configuration['local']['config_file']

    print('Checking node config file {0}'.format(config_file))

    with open(config_file, 'r') as fp:
        config = fp.read()
        check = config_check(config, config_file)

        # compulsory
        check(r'^ISTANBUL_BLOCKPERIOD=\"--istanbul.blockperiod \d\"$')
        check(r'^SYNCMODE=\"--syncmode full\"$')
        check(r'^MINE=\"--mine\"$')
        check(r'^MINERTHREADS=\"--minerthreads 1\"$')

        check(r'--rpcapi [\w\W]*istanbul')

        # don't repeat other checks done during raft

    print('==== PASS ====')

    '''
    check('^CONSTELLATION_IPC_FILE_DIR=$')

    check('^EMITCHECKPOINTS=\'--emitcheckpoints\'$') # istanbul

    $RAFTJOINEXISTING
    $RPCCORSDOMIAN $UNLOCK $PASSWORD
    $TARGETGASLIMIT

    $SHH $WS $WSADDR $WSPORT $WSAPI $WSORIGINS $NAT
    '''


if sys.argv[1] == 'raft':
    test_raft_quorum_node()
else:
    test_ibft_quorum_node()
