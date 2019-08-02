import json
import os
from psutil import signal
from time import sleep

import psutil
import sh

from quorumtoolbox.tessera import Tessera


def find_tessera(runport):
    for process in psutil.process_iter():
        if 'java' == process.name():
            for cmdline in process.cmdline():
                if 'tessera' in cmdline:
                    if process.connections() and process.connections()[0].laddr.port == int(runport):
                        return process

    return None


def kill_tessera():
    for proc in psutil.process_iter():
        if 'java' in proc.name():
            for cmdline in proc.cmdline():
                if 'tessera' in cmdline:
                    print("Killing...")
                    proc.send_signal(signal.SIGTERM)
                    sleep(10)
                    print('Pid {0} killed'.format(proc.pid))
                    return

def change_test_paths(config_file):
    with open(config_file, 'r') as cf:
        inp = cf.read()

    inp = json.loads(inp)
    #check_ipc_len(inp['serverConfigs'][0]['serverAddress'])  # if need to check ipc len in original config
    test_path = os.path.dirname(os.path.realpath(config_file))

    inp['jdbc']['url'] = 'jdbc:h2:' + os.path.join(test_path, 'db') + ';MODE=Oracle;TRACE_LEVEL_SYSTEM_OUT=0'
    inp['serverConfigs'][0]['serverAddress'] = 'unix:' + os.path.join(test_path, 'tessera.ipc')
    #inp['serverConfigs'][0]['serverAddress'] = 'unix:' + os.path.join('/short/path', 'tessera.ipc')
    inp['serverConfigs'][1]['sslConfig']['serverKeyStore'] = os.path.join(test_path, 'server-keystore')
    inp['serverConfigs'][1]['sslConfig']['knownClientsFile'] = os.path.join(test_path, 'knownClients')
    inp['serverConfigs'][1]['sslConfig']['clientKeyStore'] = os.path.join(test_path, 'client-keystore')
    inp['serverConfigs'][1]['sslConfig']['knownServersFile'] = os.path.join(test_path, 'knownServers')
    inp['keys']['keyData'][0]['privateKeyPath'] = os.path.join(test_path, 'keys', 'node.key')
    inp['keys']['keyData'][0]['publicKeyPath'] = os.path.join(test_path, 'keys','node.pub')

    with open(config_file, 'w') as cf:
        cf.write(json.dumps(inp))

    check_ipc_len(inp['serverConfigs'][0]['serverAddress'])

def check_ipc_len(ipc):
    if len(ipc) > 64:
        raise Exception("ipc file ({0}) length ({1}) in config file is too high. This may lead to bind errors when tessera is launched.".format(ipc, len(ipc)))

print('====== START TESSERA TEST =======')
context = 'company1_q2_n0'
t_port = 9000
other_nodes = ['https://localhost:9001']

cn = Tessera(context, 'https://localhost', port=t_port, other_nodes=other_nodes)

print('Created all artifacts and keys need for tessera node. Ready to be launched.')

print('\nKilling any running tessera...')
kill_tessera()

print('Launching tessera...')

tessera_config_file = os.path.join(context, 'tessera', 'tessera.json')
change_test_paths(tessera_config_file)

bin = os.path.join(os.environ['TESSERA_LOC'], 'tessera')
cmd = sh.Command('java').bake('-jar', bin, '-configfile', tessera_config_file)
for other_node in other_nodes:
    cmd = cmd.bake('--peer.url', other_node)

cmd(_bg=True)

print('Done')
print('\nChecking...')
sleep(10)  # give some time for tessera to start up

port = ''
with open(tessera_config_file, 'r') as fp:
    port = json.loads(fp.read())["serverConfigs"][1]["serverAddress"].split(":")[2]

print('Looking for tessera running at port {0}'.format(port))

tessera_process = find_tessera(port)


if not tessera_process:
    raise Exception('Unable to find tessera running')

print('Shutting tessera')
tessera_process.send_signal(signal.SIGTERM)

print('====== PASS =======')
