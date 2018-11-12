from create_quorum_node import CreateQuorumNode

print("Creating initial node for new Quorum network")

context = input("Enter a name for this node (e.g. acme_corp_nwk1_node0):  ")
address = input("Enter the public facing IP for this node:  ")

node_params = {
    'context': context,
    'address': address,
    'node_state': "initial"
}

qn = CreateQuorumNode(node_params)

print("Created artifacts in folder: {0}. Note the following:\n 1. Network id: {1}\n 2. Constellation Url: {2}\n"
            .format(context, qn.networkid, qn.ptm_url))

networkid = qn.networkid
genesis_content = qn.genesis_content

input("!! Please deploy the initial node before creating further nodes.")

while True:
    if input("\nWould you like to create a new node in the network?. Enter 0 to exit or anything else to continue:  ") == "0":
        break

    context = input("Enter a name for this node (e.g. acme_corp_nwk1_node1):  ")
    new_address = input("Enter the public facing IP for this node:  ")

    node_params = {
        'context': context,
        'address': new_address,
        'node_state': "new",
        'networkid': networkid
    }

    network_params = {
        'genesis_content': genesis_content,
        'other_raft_public_ip': address,
        'other_constellation_public_ip': address
    }

    qn = CreateQuorumNode(node_params, network_params)

    print("Created artifacts for new node with joining ID {0}".format(qn.consensus_id))
    print("Created artifacts in folder: {0}. Note the following:\n 1. Join id: {1}\n 2. Constellation Url: {2}\n \
3. Constellation peer url: {3}".format(context, qn.consensus_id, qn.ptm_url, qn.ptm_peers))

print("Bye")