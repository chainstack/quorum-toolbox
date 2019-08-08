import json
import random
import requests

from quorumtoolbox.utils.common import make_url


def get_raft_joining_id(peers, enode_id):
    if not peers:
        raise ValueError('RAFT peer list is empty')

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

        try:
            res = requests.post(address, json=body)
            raft_joining_id = json.loads(res.text)['result']
            break
        except Exception as e:
            print(e)

    if not raft_joining_id:
        raise Exception('Tried all peers...unable to get raft joining id.')

    print('Received Raft Join Id {0} for {1}'.format(raft_joining_id, enode_id))
    return raft_joining_id
