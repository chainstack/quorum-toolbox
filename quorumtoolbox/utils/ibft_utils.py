import random
import requests

from quorumtoolbox.utils.common import make_url


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

        try:
            result = requests.post(address, json=body)
            break
        except Exception as e:
            print(e)

    if not result or result.status_code != 200:
        print(result)
        raise Exception('Tried all peers...unable to add node to existing ibft network.')

    print('Added ibft node: {0} to existing ibft network'.format(enode_id_geth))
