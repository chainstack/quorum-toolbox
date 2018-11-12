import json

from quorum_network import QuorumNetwork

constellation_params = {
    'other_nodes': []
    #'other_nodes': ["https://35.240.155.184:9000"]
}

raft_params = {
    'peers': []
    #'peers': ["35.240.155.184"]
}

geth_params = {
    'max_peers': 250
}

node_options = {
    'no_of_nodes': 1,
    'networkid': 1981,
    'contexts': ["company1_q2_n0"],
    'addresses': ["10.65.11.96"],
    'rpcaddrs': ["0.0.0.0"],
    'node_state': "initial",
    'genesis_content': "",
    'consensus': "raft",
    'consensus_params': raft_params,
    'private_manager': "constellation",
    'private_manager_params': constellation_params,
    'geth_params': geth_params
}

genesis_params = {
  "coinbase": "0x0000000000000000000000000000000000000000",
  "config": {
    "byzantiumBlock": 1,
    "chainId": node_options['networkid'],
    "eip150Block": 1,
    "eip155Block": 0,
    "eip150Hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "eip158Block": 1,
    "isQuorum":True
  },
  "difficulty": "0x0",
  "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "gasLimit": "0xE0000000",
  "mixhash": "0x00000000000000000000000000000000000000647572616c65787365646c6578",
  "nonce": "0x0",
  "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "timestamp": "0x00"
}

# TODO Read genesis.json created for initial nodes and set as genesis content for new nodes
if node_options['node_state'] == "new":
    node_options['genesis_content']= json.dumps(genesis_params)

print("==== START QUORUM NETWORK TEST ====")

print("Creating {2} node Quorum network (id: {3}) with consensus: {0} and private manager: {1}"
      .format(node_options['consensus'],
              node_options['private_manager'],
              node_options['no_of_nodes'],
              node_options['networkid']))

qn = QuorumNetwork(node_options['no_of_nodes'],
                   node_options['networkid'],
                   node_options['contexts'],
                   node_options['addresses'],
                   node_options['rpcaddrs'],
                   node_options['node_state'],
                   genesis_content = node_options['genesis_content'],
                   geth_params=node_options['geth_params'],
                   consensus_params=node_options['consensus_params'],
                   private_manager_params=node_options['private_manager_params'])

static_nodes_files = qn.build_configuration['local']['static_nodes_files']
genesis_files = qn.build_configuration['local']['genesis_files']
enode_ids = qn.build_configuration['network']['enode_ids']
accounts = qn.build_configuration['network']['accounts']

if node_options['node_state'] == "initial" and len(static_nodes_files) != node_options['no_of_nodes']:
    raise Exception("Expected {0} number of static nodes file, found {1}".
                    format(node_options['no_of_nodes'], len(static_nodes_files)))

if len(genesis_files) != node_options['no_of_nodes']:
    raise Exception("Expected {0} number of genesis files, found {1}".format(node_options['no_of_nodes'], len(genesis_files)))

if len(enode_ids) != node_options['no_of_nodes']:
    raise Exception("Expected {0} number of enode ids, found {1}".format(node_options['no_of_nodes'], len(enode_ids)))

if len(accounts) != node_options['no_of_nodes']:
    raise Exception("Expected {0} number of accounts, found {1}".format(node_options['no_of_nodes'], len(accounts)))

for static_node_file in static_nodes_files:
    with open(static_node_file) as fp:
        static_nodes = json.loads(fp.read())
        if len(static_nodes) != node_options['no_of_nodes']:
            raise Exception("Expected {0} number of static nodes, found {1} in file {2}"
                            .format(node_options['no_of_nodes'], len(static_nodes), static_node_file))

        for static_node, enode_id in zip(static_nodes, enode_ids):
            if static_node != enode_id:
                raise Exception("Static node {0} and enode id {1} don't tally in file {2}"
                                .format(static_node, enode_id, static_node_file))

for genesis_file in genesis_files:
    with open(genesis_file, "r") as fp:
        genesis_content_f = json.loads(fp.read())

        if node_options['node_state'] == "new":
            if genesis_content_f != node_options['genesis_content']:
                raise Exception("Genesis content of new node {0} in file {2} does not match initial genesis content {1}".
                                format(genesis_content_f, node_options['genesis_content'], genesis_file))
        else:
            accounts_balances = genesis_content_f['alloc']

            if len(accounts_balances) != len(accounts):
                raise Exception("Expected {0} number of accounts, found {1} in genesis file {2}".
                                format(len(accounts), len(accounts_balances), genesis_file))

            for account in accounts:
                if account not in accounts_balances:
                    raise Exception("Unable to find account {0} in list of account {1} in genesis file {2}"
                                    .format(account, accounts_balances, genesis_file))

            genesis_content_f.pop('alloc')

            if genesis_content_f != genesis_params:
                print("The following entries difffer: ")
                for key, value in genesis_content_f.items():
                    if value != genesis_params.get(key, None):
                        print(key, value)

                for key, value in genesis_params.items():
                    if value != genesis_content_f.get(key, None):
                        print(key, value)

                raise Exception("Genesis content {0} in file {2} does not match expected content {1}".
                                format(genesis_content_f, genesis_params, genesis_file))


# TODO Obtain enode from nodekey: /usr/local/bin/bootnode -nodekeyhex the_nodekey -writeaddress
# use this to check created nodekeys and enode

print("==== PASS ====")