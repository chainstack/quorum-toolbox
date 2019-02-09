from quorumtoolbox import ibft
from quorumtoolbox.utils.node_utils import make_node_param

# ---------------------- Test: Non defaults
print('==== START IBFT TEST ====')

test_d = {
    'context': 'company1_q2_n0',
    'block_time': 5,
    'peers': ['10.65.11.96'],
    'enode_id':
        'enode://b5790239b648470dfd3b01227f0cfef145b1633a4d11fd3f2ac5f15d0f92d58a311955ab0c6b81f215b9e0fbd19ea0\
451434046b4a7e58c26c74958e68443f8c@172.13.0.2:30303?discport=0',
    'node_state': 'initial_ibft'
}

print('Testing ibft non default parameters...')
i = ibft.Ibft(test_d['context'],
              test_d['enode_id'],
              test_d['node_state'],
              test_d['block_time'],
              test_d['peers']
              )

ibft_build_configuration = i.build_configuration
ibft_launch_params = i.launch_parameters

print('Checking launch parameters')
if ibft_launch_params.get('istanbul_blockperiod') != make_node_param('--istanbul.blockperiod', test_d['block_time']):
    print(ibft_launch_params)
    raise Exception('--istanbul.blockperiod flag error')

if ibft_launch_params.get('syncmode') != make_node_param('--syncmode', 'full'):
    print(ibft_launch_params)
    raise Exception('--syncmode flag error')

if ibft_launch_params.get('mine') != '--mine':
    print(ibft_launch_params)
    raise Exception('--mine error')

if ibft_launch_params.get('minerthreads') != make_node_param('--minerthreads', 1):
    print(ibft_launch_params)
    raise Exception('--minerthreads error')

if ibft_launch_params.get('rpcapi') != make_node_param('--rpcapi', 'istanbul'):
    print(ibft_launch_params)
    raise Exception('--rpcapi error')

print('Checking build configuration')
if ibft_build_configuration['network']['peers'] != test_d['peers']:
    print(ibft_launch_params)
    raise Exception('Peers expected {0} and actual {1} dont tally'.
                    format(test_d['peers'], ibft_build_configuration['network']['peers']))

# ---------------------- Test: Defaults
test_d = {
    'context': 'company1_q2_n0',
    'enode_id':
        'enode://b5790239b648470dfd3b01227f0cfef145b1633a4d11fd3f2ac5f15d0f92d58a311955ab0c6b81f215b9e0fbd19ea0\
451434046b4a7e58c26c74958e68443f8c@172.13.0.2:30303?discport=0',
    'node_state': 'initial_ibft'
}

print('Testing ibft default parameters...')
i = ibft.Ibft(test_d['context'],
              test_d['enode_id'],
              test_d['node_state']
              )

ibft_build_configuration = i.build_configuration
ibft_launch_params = i.launch_parameters

print('Checking launch parameters')
if ibft_launch_params.get('istanbul_blockperiod') != make_node_param('--istanbul.blockperiod', 1):
    print(ibft_launch_params)
    raise Exception('--istanbul.blockperiod flag error')

if ibft_launch_params.get('syncmode') != make_node_param('--syncmode', 'full'):
    print(ibft_launch_params)
    raise Exception('--syncmode flag error')

if ibft_launch_params.get('mine') != '--mine':
    print(ibft_launch_params)
    raise Exception('--mine error')

if ibft_launch_params.get('minerthreads') != make_node_param('--minerthreads', 1):
    print(ibft_launch_params)
    raise Exception('--minerthreads error')

if ibft_launch_params.get('rpcapi') != make_node_param('--rpcapi', 'istanbul'):
    print(ibft_launch_params)
    raise Exception('--rpcapi error')

print('Checking build configuration')
if ibft_build_configuration['network']['peers']:
    print(ibft_launch_params)
    raise Exception('Peers expected {0} and actual {1} dont tally'.
                    format([], ibft_build_configuration['network']['peers']))

print('==== PASS ====')
