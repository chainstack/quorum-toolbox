import json
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


def generate_constellation_key(key_name):
    """
    Generate constellation key pair files. key_name is name of key pair to generate, which can include a path.

    Produces two files: .pub and .key.
    Bash command that is executed: constellation-node --genratekeys=key_name
    Currently there is no support to specify a password for locking the key files.

    :param key_name: Key pair name. e.g. node, temp/node etc.
    :return: Three parameters: Bash Exit Code, STDOUT, STDERR
    Exit code 0 is success.
    """

    cmd = sh.Command("constellation-node").bake(generatekeys=key_name, _in="\n")  # at pw prompt, enter null in stdin.
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
        raise Exception("Looks like constellation already running on port {0} with pid {1}".format(port, pid))

    cmd = sh.Command("constellation-node").bake(launch_configuration_file, _err=log_file, _cwd=cwd, _bg=True)
    run_cmd(cmd)

    sleep(5)


# TODO: Have this function launch constellation via the instance launch script
def run_launch_script():
    pass


def check_if_constellation_running(port):
    cmd = sh.netstat.bake("-lupnt")
    result = run_cmd(cmd)

    stdout = result['stdout']
    r = re.compile(":" + str(port) + " ")

    for line in stdout.split("\n"):
        if r.search(line):
            return line.split(" ")[-1].split("/")[0]

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

    cmd = sh.Command("bootnode").bake("-genkey", nodekey_file, "-writeaddress")
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

    cmd = sh.Command("bootnode").bake("-nodekey", nodekey_file, "-writeaddress")
    result = run_cmd(cmd)

    enode = result['stdout'].replace("\n", "")

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

    cmd = sh.Command("geth").bake("--password", passwords_file, "account", "new", datadir=store_dir)
    result = run_cmd(cmd)

    # Extract the address from stdout
    # e.g: 'Address: {4ce81fd2e8130716cad503f05bad7eb00d7f0c56}'
    stdout = result['stdout']
    r = re.compile("Address: {([0-9A-Za-z]+)}")
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
    # e.g. --rpcapi raft and --rpcapi admin,db,eth will be contantenated to --rpcapi raft,admin,db,eth
    if key == "rpcapi":
        return ",".join([value1, value2.replace("--rpcapi", "").replace(" ", "")])

    raise Exception("Unknown duplicate parameter {0}".format(key))

    # add any more special cases as needed


def make_quorum_node_launch_config(launch_params):
    lines = "#!/bin/bash" + "\n\n"  # use bash

    for key, value in launch_params.items():
        lines += key.upper() + "=" + json.dumps(value) + "\n"  # e.g DATADIR="--datadir qdata/dd"

    return lines


def write_quorum_node_launch_config(launch_params, config_file):
    content = make_quorum_node_launch_config(launch_params)
    fs_utils.write_file(config_file, content)
