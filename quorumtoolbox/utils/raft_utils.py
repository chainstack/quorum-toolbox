# Why isint this file inside /utils?
import json
import random
import re

import requests


# TODO: any existing RPC library available, instead of ROW?
def get_raft_joining_id(peers, enode_id):
    if not peers:
        raise Exception('Need to obtain raft joining id, but peer list is empty!')

    raft_joining_id = None

    for peer in peers:
        address = make_url(peer)
        print('RPC call to {0} for Raft Join Id for {1}'.format(address, enode_id))

        body = {
            'jsonrpc': '2.0',
            'method': 'raft_addPeer',
            'params': [enode_id],
            'id': random.randint(1, 1000000)
        }

        # TODO direct data=body dont seem to work for GO API. Why? something to do with " vs ' when representing string
        try:
            res = requests.post(address, json=body)
            raft_joining_id = json.loads(res.text)['result']
        except Exception:
            continue
        else:
            break  # break on getting first valid raft id from network

    if raft_joining_id is None:
        raise Exception('Tried all peers...unable to get raft joining id.')
        # TODO: Need better error propogation as this step is crucial

    print('Received Raft Join Id {0} for {1}'.format(raft_joining_id, enode_id))
    return raft_joining_id  # An integer


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
