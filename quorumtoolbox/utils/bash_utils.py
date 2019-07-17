import json
import os
import re
from time import sleep

import sh

from quorumtoolbox.utils import fs_utils


def run_cmd(cmd):
    result = cmd()  # bubble up exception

    return {
        'exit_code': result.exit_code,
        'stdout': sh_output_to_str(result.stdout),
        'stderr': sh_output_to_str(result.stderr)
    }


def generate_tessera_key(key_name):
    # at pw prompt, enter null in stdin.
    # tessera keygen doesn't seem to accept relative paths
    file_name = os.path.split(key_name)[1]
    file_loc = os.path.split(key_name)[0] if os.path.split(key_name)[0] != '' else None

    cmd = sh.Command('java').bake('-jar', '/usr/local/bin/tessera',
                                  '-keygen',
                                  '-filename', file_name,
                                  _cwd=file_loc,
                                  _in='\n')
    result = run_cmd(cmd)

    return result['stdout']


def generate_constellation_key(key_name):
    """
    Generate constellation key pair files. key_name is name of key pair to generate, which can include a path.

    Produces two files: .pub and .key.
    Bash command that is executed: constellation-node --generatekeys=key_name
    Currently there is no support to specify a password for locking the key files.

    :param key_name: Key pair name. e.g. node, temp/node etc.
    :return: Three parameters: Bash Exit Code, STDOUT, STDERR
    Exit code 0 is success.
    """

    cmd = sh.Command('constellation-node').bake(generatekeys=key_name, _in='\n')  # at pw prompt, enter null in stdin.
    result = run_cmd(cmd)

    return result['stdout']


# when launched in background, redirection of stderr to file seems to work only till calling python script is executing.
# So, if calling python script exists immediately, though constellation is running in background, its stderr redirection
# stops. So, just put a small sleep so that any errors, at-least at startup, is redirected to file. Redirection will
# stop once the calling python script exists. Constellation will continue to run though.
# TODO: Need to investigate this
def launch_constellation(launch_configuration_file, log_file, cwd=None, port=9000):
    pid = check_if_constellation_running(port)
    if pid is not None:
        raise Exception('Looks like constellation already running on port {0} with pid {1}'.format(port, pid))

    cmd = sh.Command('constellation-node').bake(launch_configuration_file, _err=log_file, _cwd=cwd, _bg=True)
    run_cmd(cmd)

    sleep(5)


# TODO: Have this function launch constellation via the instance launch script
def run_launch_script():
    pass


def check_if_constellation_running(port):
    cmd = sh.netstat.bake('-lupnt')
    result = run_cmd(cmd)

    stdout = result['stdout']
    r = re.compile(':' + str(port) + ' ')

    for line in stdout.split('\n'):
        if r.search(line):
            return line.split(' ')[-1].split('/')[0]

    return None


def sh_output_to_str(inp):
    return inp.decode(sh.DEFAULT_ENCODING)


def generate_nodekey_and_enode(nodekey_file):
    nodekey = generate_nodekey(nodekey_file)
    enode = generate_enode(nodekey_file)

    return nodekey, enode


def generate_nodekey(nodekey_file):
    """
    Generate a new nodekey for a geth node and store in a file.

    Bash command that is executed: bootnode -genkey nodekey_file -writeaddress

    :param: nodekey_file: file where node's nodekey is to be stored.
    :return: Three parameters: Bash Exit Code, STDOUT, STDERR
    Exit code 0 is success.
    """

    cmd = sh.Command('bootnode').bake('-genkey', nodekey_file, '-writeaddress')
    run_cmd(cmd)

    nodekey = fs_utils.read_file(nodekey_file)

    return nodekey


def generate_enode(nodekey_file):
    """
    Generate enode of a geth node from its nodekey file.

    Bash command that is executed: bootnode -nodekey nodekey_file -writeaddress

    :param: nodekey_file: file where node's nodekey is stored.
    :return: Three parameters: Bash Exit Code, generated enode on success, STDERR
    Exit code 0 is success.
    """

    cmd = sh.Command('bootnode').bake('-nodekey', nodekey_file, '-writeaddress')
    result = run_cmd(cmd)

    enode = result['stdout'].replace('\n', '')

    return enode


def generate_geth_account(store_dir, passwords_file):
    """
    Generate a geth account, the account related info will be placed in store_dir/keystore. keystore directory will be
    created if non existent.

    Bash command that is executed: geth --password passwords_file account new --datadir=store_dir

    :param: store_dir: location where keystore directory will be created (if not already present). Account related
    file will be placed within keystore. Each account is identified by a single file.
    :return: Three parameters: Bash Exit Code, STDOUT (this will be the generated account's address on success), STDERR
    Exit code 0 is success.
    """

    cmd = sh.Command('geth').bake('--password', passwords_file, 'account', 'new', datadir=store_dir)
    result = run_cmd(cmd)

    # Extract the address from stdout
    # e.g: 'Address: {4ce81fd2e8130716cad503f05bad7eb00d7f0c56}'
    stdout = result['stdout']
    r = re.compile(r'Address: {([0-9A-Za-z]+)}')
    o = r.search(stdout)

    return o.group(1)


def make_quorum_node_launch_params(list_of_kv):
    launch_params = {}

    for kv in list_of_kv:
        for key, value in kv.items():
            if key not in launch_params:
                launch_params[key] = value
            else:
                launch_params[key] = handle_duplicate_launch_params(key, launch_params[key], value)

    return launch_params


def handle_duplicate_launch_params(key, value1, value2):
    # e.g. --rpcapi raft and --rpcapi admin,db,eth will be concatenated to --rpcapi raft,admin,db,eth
    if key == 'rpcapi':
        return ','.join([value1, value2.replace('--rpcapi', '').replace(' ', '')])

    raise Exception('Unknown duplicate parameter {0}'.format(key))

    # add any more special cases as needed


def make_quorum_node_launch_config(launch_params):
    lines = '#!/bin/bash' + '\n\n'  # use bash

    for key, value in launch_params.items():
        lines += key.upper() + '=' + json.dumps(value) + '\n'  # e.g DATADIR='--datadir qdata/dd'

    return lines


def write_quorum_node_launch_config(launch_params, config_file):
    content = make_quorum_node_launch_config(launch_params)
    fs_utils.write_file(config_file, content)


def generate_ibftaddress_nodekey_enode(nodekey_file):
    """
        Generate the following: ibft address, geth nodekey (save this in nodekey_file) and geth enode.

        Bash command that is executed: istanbul setup --num 1 --nodes --verbose

        :param: nodekey_file: file where node's nodekey is to be stored.
        :return: Three parameters: ibft address, nodekey and enode
        """

    cmd = sh.Command('istanbul').bake('setup', '--num', '1', '--nodes', '--verbose')
    result = run_cmd(cmd)

    stdout = result['stdout']

    ibft_address = parse_ibft_address(stdout)
    nodekey = parse_node_key(stdout)
    enode = parse_enode(stdout)

    fs_utils.write_file(nodekey_file, nodekey)

    return ibft_address, nodekey, enode


def generate_ibft_extradata(ibft_addresses):
    """
    Generate genesis extradata for ibft.

    Bash command that is executed: istanbul extra encode --vanity 0x00 --validators 0xibftaddr1,0xibftaddr2...

    :param: ibft_addrs: a list of ibft addresses
    :return: extradata: for use in genesis content
    """

    validators = sort_ibft_addresses(ibft_addresses)
    cmd = sh.Command('istanbul').bake('extra', 'encode', '--vanity', '0x00',
                                      '--validators', validators)
    result = run_cmd(cmd)

    stdout = result['stdout']
    extra_data = parse_extra_data(stdout)

    return extra_data


def parse_ibft_address(input):
    # e.g. "Address": "0x256aa60787d6c0854d2498766d981c3658dfd99f"
    # ibft_address = "0x256aa60787d6c0854d2498766d981c3658dfd99f"
    ibft_regex = re.compile(r'\"Address\": \"(0x[a-z0-9A-Z]{40})\"')
    ibft_address = ibft_regex.search(input).group(1)

    return ibft_address


def parse_node_key(input):
    # e.g. "Nodekey": "4ae0c61391ddb1a194d0db4210e6a171aeca278eba27635f29f92ce98f0f86d4",
    # nodekey = "4ae0c61391ddb1a194d0db4210e6a171aeca278eba27635f29f92ce98f0f86d4"
    nodekey_regex = re.compile(r'\"Nodekey\": \"([a-z0-9A-Z]{64})\"')
    nodekey = nodekey_regex.search(input).group(1)

    return nodekey


def parse_enode(input):
    # e.g. "NodeInfo": "enode://e51b506fcddce909027df77bb48980b38c4a323d0f5c644de88e4f22b26b5a3b0e4c088a4dd5712fdf3ff29
    # 46c89fa3d537e39789161c97b1d32a31d18e74dad@0.0.0.0:30303?discport=0"
    # enode = "e51b506fcddce909027df77bb48980b38c4a323d0f5c644de88e4f22b26b5a3b0e4c088a4dd5712fdf3ff2946c89fa3d537e3978
    # 9161c97b1d32a31d18e74dad"
    enode_regex = re.compile(r'\"NodeInfo\": \"enode://([a-z0-9A-Z]{128})')
    enode = enode_regex.search(input).group(1)

    return enode


def sort_ibft_addresses(ibft_addresses):
    # e.g. convert ['0x7d8299de61faed3686ba4c4e6c3b9083d7e2371', '0x475cc98b5521ab2a1335683e7567c8048bfe79ed'] to
    # [44783521692591246147530128130371968073130189681, 407407570268637906433216223294237923495647279597] and then sort
    ibft_addresses = [int(address, 16) for address in ibft_addresses]
    ibft_addresses.sort()

    # convert back to hex and pad to proper length
    result = []
    for address in ibft_addresses:
        result.append(pad_ibft_address(hex(address)))

    return result


def pad_ibft_address(address):
    if len(address) > 42:
        raise Exception('Something is wrong...ibft address {0} is > 42 in length'.format(address))

    pad_len = 42 - len(address)

    # e.g. address 0x7d8299de61faed3686ba4c4e6c3b9083d7e2371 padded to length 42 as
    # 0x07d8299de61faed3686ba4c4e6c3b9083d7e2371
    return ''.join(['0x', '0' * pad_len, address.split('0x')[1]])


def parse_extra_data(input):
    # e.g. Encoded Istanbul extra-data: 0x0000000000000000000000000000000000000000000000000000000000000000f89af85494475c
    # c98b5521ab2a1335683e7567c8048bfe79ed9407d8299de61faed3686ba4c4e6c3b9083d7e2371944fe035ce99af680d89e2c4d73aca01dbfc
    # 1bd2fd94dc421209441a754f79c4a4ecd2b49c935aad0312b84100000000000000000000000000000000000000000000000000000000000000
    # 00000000000000000000000000000000000000000000000000000000000000000000c0

    # extradata = Encoded Istanbul extra-data: 0x0000000000000000000000000000000000000000000000000000000000000000f89af85
    # 494475cc98b5521ab2a1335683e7567c8048bfe79ed9407d8299de61faed3686ba4c4e6c3b9083d7e2371944fe035ce99af680d89e2c4d73ac
    # a01dbfc1bd2fd94dc421209441a754f79c4a4ecd2b49c935aad0312b8410000000000000000000000000000000000000000000000000000000
    # 000000000000000000000000000000000000000000000000000000000000000000000000000c0
    extradata_regex = re.compile(r'Encoded Istanbul extra-data: (0x[a-z0-9A-Z]+)')
    extradata = extradata_regex.search(input).group(1)

    return extradata
