import json
import os
import re
from unittest import mock

from quorumtoolbox.geth import Geth
from quorumtoolbox.utils.bash_utils import generate_geth_account
from quorumtoolbox.utils.node_utils import make_node_param


def check_ibft_address(ibft_address):
    regex = re.compile(r'^0x[a-z0-9A-Z]{40}$')
    output = regex.search(ibft_address)
    if not output:
        raise Exception('Improper ibft address {0}'.format(ibft_address))


def check_geth_new_account():
    result = mock.Mock()
    result.stdout = ('\nYour new key was generated\n'
                     '\nPublic address of the key:   0xaA1Fc2A219f74492d4ef10B1445c6cade3A896DC'
                     '\nPath of the secret key file: /tmp/pytest-of-root/pytest-2/'
                     'test_quorum_generate_node_para0/networks/nw-434-4563/ND-000/'
                     'blockchain/qdata/dd/keystore/UTC--2020-05-19T06-21-28.'
                     '681398400Z--aa1fc2a219f74492d4ef10b1445c6cade3a896dc\n\n- '
                     'You can share your public address with anyone. Others need'
                     ' it to interact with you.\n- You must NEVER share the secret key '
                     'with anyone! The key controls access to your funds!\n- '
                     'You must BACKUP your key file! Without the key, it\'s impossible '
                     'to access account funds!\n- You must REMEMBER your password! '
                     'Without the password, it\'s impossible to decrypt the key!\n\n').encode()
    result.stderr = b''
    result.exit_code = 0

    with mock.patch('sh.Command.bake', return_value=mock.Mock(return_value=result)):
        assert generate_geth_account(mock.Mock(), mock.Mock()) == 'aa1fc2a219f74492d4ef10b1445c6cade3a896dc'


def check_accounts(geth_i, no_of_accounts):
    keystore_dir = geth_i.build_configuration['local']['keystore_dir']

    count = 0
    found = 0
    for root, dirs, files in os.walk(keystore_dir):
        for filename in files:
            if 'UTC' in filename:
                count += 1

            with open(os.path.join(root, filename), 'r') as fp:
                try:
                    account_json = json.loads(fp.read())
                    if account_json['address'] == geth_i.accounts[0]:
                        found += 1
                except Exception:
                    continue

            print('Deleting account key file {0} as part of test.'.format(os.path.join(root, filename)))
            os.remove(os.path.join(root, filename))

    if count != no_of_accounts:
        raise Exception('Expected one account file, found {0}'.format(count))

    if found == 0:
        raise Exception('Unable to find account {0} in keystore file.'.format(geth_i.accounts[0]))

    if found != no_of_accounts:
        raise Exception(
            'Expected account {0} to be in one file only, found in multiple files.'.format(geth_i.accounts[0]))

    if no_of_accounts != geth_i.no_of_accounts:
        raise Exception('Expected {0} number of accounts, got {1}.'.format(no_of_accounts, geth_i.no_of_accounts))


# ---------------------- Test: Non defaults
print('==== START GETH TEST ====')

print('Testing geth new account cmd...')
check_geth_new_account()

test_param = {
    'context': 'company1_q2_n0',
    'addr': '127.0.0.1',
    'rpcaddr': '10.65.11.96',
    'network_id': 1981,
    'port': 5000,
    'rpcport': 9999,
    'max_peers': 100
}

print('Testing geth non default parameters...')
geth = Geth(test_param['context'],
            test_param['addr'],
            test_param['rpcaddr'],
            test_param['network_id'],
            port=test_param['port'],
            rpcport=test_param['rpcport'],
            max_peers=test_param['max_peers'])

print('Checking nodekey ...')
build_config = geth.build_config

nodekey_file = build_config['local']['nodekey_file']
with open(nodekey_file, 'r') as fp:
    nodekey = fp.read()
    if len(nodekey) != 64:
        raise Exception('Generated nodekey {0} in file {1} is of incorrect length {2}, expected {3}'
                        .format(nodekey, nodekey_file, len(nodekey), 64))

print('Checking enode and enode_id_geth')
enode = build_config['network']['enode']
enode_id_geth = build_config['network']['enode_id_geth']

if len(enode) != 128:
    raise Exception('Generated enode {0} is of incorrect length {1}, expected {2}'.format(enode, len(enode), 128))

# 'enode://35cf975685f7aae0a6a70c80f536e6259e2898e23fcd5b3752924dec50c88b9d6b7e7c889632f37e2af3589cdd4f4c2e8081e3869f4024\
# a7cf7370aecab58d74@172.13.0.2:30303'
r = re.compile(r'^enode://([a-zA-Z0-9]{128,128})@([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}):([0-9]+)')
o = r.search(enode_id_geth)

if not o:
    raise Exception('Improper format of enode_id_geth {0}'.format(enode_id_geth))

if o.group(1) != enode:
    raise Exception('Enode {0} not found in enode_id_geth {1}'.format(enode, enode_id_geth))

if o.group(2) != test_param['addr']:
    raise Exception('Unable to find address {0} in enode_id_geth {1}'.format(test_param['addr'], enode_id_geth))

if o.group(3) != str(test_param['port']):
    raise Exception('Unable to find port {0} in {1} of enode_id_geth {2}'.
                    format(test_param['port'], o.group(3), enode_id_geth))

print('Checking ibft validator address')
ibft_address = build_config['network']['ibft_address']
check_ibft_address(ibft_address)

print('Checking launch params....')
launch_params = geth.launch_params

if launch_params['rpcport'] != make_node_param('--rpcport', test_param['rpcport']):
    raise Exception(
        '--rpcport is wrong in launch params {0}, expected {1}'.format(launch_params, test_param['rpcport']))

if launch_params.get('maxpeers') != make_node_param('--maxpeers', test_param['max_peers']):
    print(launch_params)
    raise Exception('--maxpeers error')

if geth.no_of_accounts != 1:
    raise Exception('Expected 1 account, got {0} accounts'.format(geth.no_of_accounts))

check_accounts(geth, 1)
# ---------------------- Test: defaults
print('Testing geth default parameters...')
geth = Geth(test_param['context'],
            test_param['addr'],
            test_param['rpcaddr'],
            test_param['network_id'])

print('Checking nodekey ...')
build_config = geth.build_config

nodekey_file = build_config['local']['nodekey_file']
with open(nodekey_file, 'r') as fp:
    nodekey = fp.read()
    if len(nodekey) != 64:
        raise Exception('Generated nodekey {0} is of incorrect length {1}, expected {2}'.format(
            nodekey, len(nodekey), 64))

print('Checking enode and enode_id_geth')
enode = build_config['network']['enode']
enode_id_geth = build_config['network']['enode_id_geth']

if len(enode) != 128:
    raise Exception('Generated enode {0} is of incorrect length {1}, expected {2}'.format(enode, len(enode), 128))

# 'enode://35cf975685f7aae0a6a70c80f536e6259e2898e23fcd5b3752924dec50c88b9d6b7e7c889632f37e2af3589cdd4f4c2e8081e3869f4024\
# a7cf7370aecab58d74@172.13.0.2:30303'
r = re.compile(r'^enode://([a-zA-Z0-9]{128,128})@([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}):([0-9]+)')
o = r.search(enode_id_geth)

if not o:
    raise Exception('Improper format of enode_id_geth {0}'.format(enode_id_geth))

if o.group(1) != enode:
    raise Exception('Enode {0} not found in enode_id_geth {1}'.format(enode, enode_id_geth))

if o.group(2) != test_param['addr']:
    raise Exception('Unable to find address {0} in enode_id_geth {1}'.format(test_param['addr'], enode_id_geth))

if o.group(3) != '30303':
    raise Exception('Default port 30303 not in enode_id_geth {0}'.format(enode_id_geth))

print('Checking launch params....')
launch_params = geth.launch_params

if launch_params['rpcport'] != make_node_param('--rpcport', 8545):
    raise Exception('--rpcport is wrong in launch params {0}, expected {1}'.format(launch_params, 8545))

if launch_params.get('maxpeers') != make_node_param('--maxpeers', 25):
    print(launch_params)
    raise Exception('--maxpeers error')

check_accounts(geth, 1)
# ---------------------------------------------------------------------------------
print('==== PASS ====')
