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


print('====== START TESSERA TEST =======')
context = 'company1_q2_n0'
t_port = 9000
other_nodes = ['https://localhost:9001']

cn = Tessera(context, 'https://localhost', port=t_port, other_nodes=other_nodes)

print('Created all artifacts and keys need for tessera node. Ready to be launched.')

print('\nKilling any running tessera...')
kill_tessera()

print('Launching tessera...')

curr_dir = os.path.abspath(os.curdir)
os.chdir(os.path.join(curr_dir, context, 'tessera'))

bin = os.path.join(os.environ['TESSERA_LOC'], 'tessera')
cmd = sh.Command('java').bake('-jar', bin, '-configfile', 'tessera.json')
for other_node in other_nodes:
    cmd = cmd.bake('--peer.url', other_node)

cmd(_bg=True)

print('Done')
print('\nChecking...')
sleep(10)  # give some time for tessera to start up

port = ''
with open('tessera.json', 'r') as fp:
    port = json.loads(fp.read())["serverConfigs"][1]["serverAddress"].split(":")[2]

print('Looking for tessera running at port {0}'.format(port))

tessera_process = find_tessera(port)


if not tessera_process:
    raise Exception('Unable to find tessera running')

print('Shutting tessera')
tessera_process.send_signal(signal.SIGTERM)

os.chdir(curr_dir)

print('====== PASS =======')
