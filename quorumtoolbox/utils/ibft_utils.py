# coding=utf-8
import random
import re

import requests


# TODO: any existing RPC library available, instead of ROW?
def join_existing_ibft_network(peers, enode_id_geth):
    if not peers:
        raise Exception('Need to join an existing ibft network, but peer list is empty!')

    result = None

    for peer in peers:
        address = make_url(peer)
        print('RPC call to {0} to add IBFT node {1}'.format(address, enode_id_geth))

        body = {
            'jsonrpc': '2.0',
            'method': 'admin_addPeer',
            'params': [enode_id_geth],
            'id': random.randint(1, 1000000)
        }

        # TODO direct data=body don't seem to work for GO API. Why? something to do with " vs ' when representing string
        # TODO need better logic. If a peer returns an invalid result, instead of breaking, try next peer.
        # TODO For ibft, perhaps its better to add new node to all peers since net.peerCount for new node only shows 1
        try:
            result = requests.post(address, json=body)
        except Exception:
            continue
        else:
            break  # break on getting first response from network

    if not result or result.status_code != 200:
        raise Exception('Tried all peers...unable to add node to existing ibft network.')
        # TODO: Need better error propagation as this step is crucial

    print('Added ibft node: {0} to existing ibft network'.format(enode_id_geth))


# TODO: 8545, the default geth RPC port, must come from some config file.
def make_url(address):
    r = re.compile(r'^http://')
    if r.match(address) is None:
        address = 'http://' + address

    # e.g. :9000 or :9000/, @ end of address
    r = re.compile(r':[0-9]+/?$')

    if r.match(address) is None:
        if address[-1] == '/':
            address = address[:-1] + ':' + '8545' + '/'
        else:
            address = address + ':' + '8545' + '/'

    return address
