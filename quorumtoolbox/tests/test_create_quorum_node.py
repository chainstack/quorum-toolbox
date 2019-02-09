"""
This script creates Quorum nodes of the following types:
1. RAFT
    a. Initial nodes
    b. New nodes
2. IBFT
    a. Initial nodes
    b. New nodes

The class CreateQuorumNode takes a parameter node_state which is set as follows:
1. initial/new: To create Raft initial or new node respectively
2. initial_ibft/new_ibft: To create Ibft initial or new node respectively

Note: For IBFT node, a validator address will be generated. Take note of this since it can be used to vote validator
proposals.
"""

from quorumtoolbox.create_quorum_node import CreateQuorumNode
from quorumtoolbox.utils import node_utils

print('Creating initial node for new Quorum network')

node_type = input('Enter \'ibft\' to create IBFT network. Leave blank for RAFT network: ')
node_state = 'initial' + '_' + node_type if node_type else 'initial'
context = input('Enter a name for this node (e.g. acme_n0):  ')
address = input('Enter the public facing IP for this node:  ')

node_params = {
    'context': context,
    'address': address,
    'node_state': node_state
}

qn = CreateQuorumNode(node_params)

print('Created artifacts in folder: {0}. Note the following:\n 1. Network id: {1}\n 2. Constellation Url: {2}\n'
      .format(context, qn.networkid, qn.ptm_url))

if node_utils.is_istanbul_node(node_state):
    print('IBFT address for the node is {0}. (Used for IBFT networks only, for voting proposals).\n'.format(
        qn.ibft_address))

networkid = qn.networkid
genesis_content = qn.genesis_content

input('!! Please deploy the initial node before creating further nodes.')

while True:
    if input(
            '\nWould you like to create a new node in the network?. Enter 0 to exit or anything else to continue:  ') \
            == '0':
        break

    node_state = 'new' + '_' + node_type if node_type else 'new'

    context = input('Enter a name for this node (e.g. acme_n1):  ')
    new_address = input('Enter the public facing IP for this node:  ')

    node_params = {
        'context': context,
        'address': new_address,
        'node_state': node_state,
        'networkid': networkid
    }

    network_params = {
        'genesis_content': genesis_content,
        'other_node_public_ip': address,
        'other_constellation_public_ip': address
    }

    qn = CreateQuorumNode(node_params, network_params)

    print('Created artifacts for new node with joining ID {0}'.format(qn.consensus_id))
    print('Created artifacts in folder: {0}. Note the following:\n 1. Join id: {1}\n 2. Constellation Url: {2}\n \
3. Constellation other nodes url: {3}\n'.format(context, qn.consensus_id, qn.ptm_url, qn.ptm_peers))

    if node_utils.is_istanbul_node(node_state):
        print('IBFT address for the node is {0}. (Used for IBFT networks only, for voting proposals).\n'.format(
            qn.ibft_address))

print('Bye')
