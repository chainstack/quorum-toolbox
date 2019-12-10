import json
import sys

from quorumtoolbox.quorum_network import QuorumNetwork
from quorumtoolbox.utils import node_utils, bash_utils

constellation_params = {
    'other_nodes': []  # e.g. ['https://35.240.155.184:9000']
}

raft_params = {
    'peers': []  # e.g. ['35.240.155.184']
}

ibft_params = {

}

geth_params = {
    'max_peers': 250
}

node_state = 'initial' if sys.argv[1] == 'raft' else 'initial_ibft'
consensus_params = raft_params if sys.argv[1] == 'raft' else ibft_params

node_options = {
    'no_of_nodes': 1,
    'networkid': 1981,
    'contexts': ['company1_q2_n0'],
    'addresses': ['10.65.11.96'],
    'rpcaddrs': ['0.0.0.0'],
    'node_state': node_state,
    'genesis_content': '',
    'consensus_params': consensus_params,
    'private_manager': 'constellation',
    'private_manager_params': constellation_params,
    'geth_params': geth_params
}

genesis_params = {
    'coinbase': '0x0000000000000000000000000000000000000000',
    'config': {
        'homesteadBlock': 0,
        'byzantiumBlock': 0,
        'constantinopleBlock': 0,
        'chainId': node_options['networkid'],
        'eip150Block': 0,
        'eip155Block': 0,
        'eip150Hash': '0x0000000000000000000000000000000000000000000000000000000000000000',
        'eip158Block': 0,
        'isQuorum': True
    },
    'difficulty': '0x0',
    'extraData': '0x0000000000000000000000000000000000000000000000000000000000000000',
    'gasLimit': '0xE0000000',
    'mixhash': '0x00000000000000000000000000000000000000647572616c65787365646c6578',
    'nonce': '0x0',
    'parentHash': '0x0000000000000000000000000000000000000000000000000000000000000000',
    'timestamp': '0x00'
}

genesis_params_ibft = {
    'coinbase': '0x0000000000000000000000000000000000000000',
    'config': {
        'homesteadBlock': 0,
        'byzantiumBlock': 0,
        'constantinopleBlock': 0,
        'chainId': node_options['networkid'],
        'eip150Block': 0,
        'eip155Block': 0,
        'eip150Hash': '0x0000000000000000000000000000000000000000000000000000000000000000',
        'eip158Block': 0,
        'isQuorum': True,
        'istanbul': {
            'epoch': 30000,
            'policy': 0
        },
    },
    'difficulty': '0x1',
    'gasLimit': '0xE0000000',
    'mixhash': '0x63746963616c2062797a616e74696e65206661756c7420746f6c6572616e6365',
    'nonce': '0x0',
    'parentHash': '0x0000000000000000000000000000000000000000000000000000000000000000',
    'timestamp': '0x00'
}


def check_raft_genesis(genesis_content_r):
    if genesis_content_r != genesis_params:
        print('The following entries differ: ')
        for key, value in genesis_content_r.items():
            if value != genesis_params.get(key):
                print(key, value)

        for key, value in genesis_params.items():
            if value != genesis_content_r.get(key):
                print(key, value)

        raise Exception('Genesis content {0} in file {2} does not match expected'
                        ' content {1}'.format(genesis_content_r, genesis_params, genesis_file))


def check_ibft_genesis(genesis_content_i, i_addresses):
    extra_data = genesis_content_i.pop('extraData')
    check_ibft_extradata(extra_data, i_addresses)

    if genesis_content_i != genesis_params_ibft:
        print('The following entries differ: ')
        for key, value in genesis_content_i.items():
            if value != genesis_params.get(key):
                print(key, value)

        for key, value in genesis_params.items():
            if value != genesis_content_i.get(key):
                print(key, value)

        raise Exception('Genesis content {0} in file {2} does not match expected'
                        ' content {1}'.format(genesis_content_i, genesis_params, genesis_file))


def check_ibft_extradata(extra_data, i_addresses):
    extra_data_g = bash_utils.generate_ibft_extradata(i_addresses)
    if extra_data != extra_data_g:
        raise Exception(
            'Extra data {0} in genesis does not match {1}'
            ' for validator set {2}'.format(
                extra_data, extra_data_g, i_addresses))


# TODO Read genesis.json created for initial nodes and set as genesis content for new nodes. For now just use
# genesis_params as new nodes aren't being tested anyway.
if node_utils.is_new_node(node_options['node_state']):
    node_options['genesis_content'] = json.dumps(genesis_params)

print('==== START QUORUM NETWORK TEST ====')

print('Creating {2} node Quorum network (id: {3}) with consensus: {0} and private manager: {1}'
      .format(sys.argv[1],
              node_options['private_manager'],
              node_options['no_of_nodes'],
              node_options['networkid']))

qn = QuorumNetwork(node_options['no_of_nodes'],
                   node_options['networkid'],
                   node_options['contexts'],
                   node_options['addresses'],
                   node_options['rpcaddrs'],
                   node_options['node_state'],
                   genesis_content=node_options['genesis_content'],
                   geth_params=node_options['geth_params'],
                   consensus_params=node_options['consensus_params'],
                   private_manager_params=node_options['private_manager_params'])

static_nodes_files = qn.build_configuration['local']['static_nodes_files']
genesis_files = qn.build_configuration['local']['genesis_files']
enode_ids = qn.build_configuration['network']['enode_ids']
accounts = qn.build_configuration['network']['accounts']
ibft_addresses = qn.build_configuration['network']['ibft_addresses']
ptm_addresses = qn.build_configuration['network']['private_manager_addresses']

if node_utils.is_initial_node(node_options['node_state']) and len(static_nodes_files) != node_options[
    'no_of_nodes']:
    raise Exception(
        'Expected {0} number of static nodes file,'
        ' found {1}'.format(node_options['no_of_nodes'], len(static_nodes_files)))

if len(genesis_files) != node_options['no_of_nodes']:
    raise Exception(
        'Expected {0} number of genesis files,'
        ' found {1}'.format(node_options['no_of_nodes'], len(genesis_files)))

if len(enode_ids) != node_options['no_of_nodes']:
    raise Exception(
        'Expected {0} number of enode ids,'
        ' found {1}'.format(node_options['no_of_nodes'], len(enode_ids)))

if len(accounts) != node_options['no_of_nodes']:
    raise Exception(
        'Expected {0} number of accounts, '
        'found {1}'.format(node_options['no_of_nodes'], len(accounts)))

if len(ptm_addresses) != node_options['no_of_nodes']:
    raise Exception(
        'Expected {0} number of PTM addresses,'
        ' found {1}'.format(node_options['no_of_nodes'], len(ptm_addresses)))


for static_node_file in static_nodes_files:
    with open(static_node_file) as fp:
        static_nodes = json.loads(fp.read())
        if len(static_nodes) != node_options['no_of_nodes']:
            raise Exception(
                'Expected {0} number of static nodes, found {1} in '
                'file {2}'.format(node_options['no_of_nodes'], len(static_nodes), static_node_file))

        for static_node, enode_id in zip(static_nodes, enode_ids):
            if static_node != enode_id:
                raise Exception(
                    'Static node {0} and enode id {1} dont tally in'
                    ' file {2}'.format(static_node, enode_id, static_node_file))

for genesis_file in genesis_files:
    with open(genesis_file, 'r') as fp:
        genesis_content_f = json.loads(fp.read())

        if node_utils.is_new_node(node_options['node_state']):  # new nodes
            if genesis_content_f != node_options['genesis_content']:
                raise Exception(
                    'Genesis content of new node {0} in file {2} does not match '
                    'initial genesis content {1}'.format(
                        genesis_content_f, node_options['genesis_content'], genesis_file))
        else:  # initial nodes
            accounts_balances = genesis_content_f['alloc']

            if len(accounts_balances) != len(accounts):
                raise Exception(
                    'Expected {0} number of accounts, found {1} in '
                    'genesis file {2}'.format(
                        len(accounts), len(accounts_balances), genesis_file))

            for account in accounts:
                if account not in accounts_balances:
                    raise Exception('Unable to find account {0} in list of account '
                                    '{1} in genesis file {2}'.format(
                        account, accounts_balances, genesis_file))

            genesis_content_f.pop('alloc')

            if node_utils.is_raft_node(node_options['node_state']):
                check_raft_genesis(genesis_content_f)
            else:
                check_ibft_genesis(genesis_content_f, ibft_addresses)

# TODO Obtain enode from nodekey: /usr/local/bin/bootnode -nodekeyhex the_nodekey -writeaddress
# use this to check created nodekeys and enode

print('==== PASS ====')
