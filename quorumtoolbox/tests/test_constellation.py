# coding=utf-8
import os
from time import sleep

import psutil
import sh

from quorumtoolbox.constellation import Constellation

print('====== START CONSTELLATION TEST =======')
cn = Constellation('company1_q2_n0',
                   'https://10.65.11.96',
                   port=9000,
                   other_nodes=['http://127.0.0.1:9000/', 'http://10.11.11.11:9000/'])

print('Created all artifacts and keys need for constellation node. Ready to be launched.')

print('\nKilling any running constellation...')

for proc in psutil.process_iter():
    if 'constellation-node' in proc.name():
        proc.kill()
        print('Pid {0} killed'.format(proc.pid))

print('Launching constellation with launch script...')
# Note: at this point, constellation can also be launched as cn.launch(), which will take care of changing cwd and etc.
# however, we launch via launch script as during final deployment this is how constellation will be launched.

# can also pass cwd to sh instead of having to change and revert cwd manually.
curr_dir = os.path.abspath(os.curdir)
os.chdir(os.path.join(curr_dir, 'company1_q2_n0', 'constellation'))

cmd = sh.Command('./launch_constellation.sh')
cmd()

print('Done')
print('\nChecking...')
sleep(5)  # give some time for constellation to start up

port = ''
with open('constellation.config', 'r') as fp:
    for line in fp:
        if 'port' in line:
            port = line.split('= ')[1].replace('\n', '')

print('Looking for constellation-node running at port {0}'.format(port))


def find_constellation_node():
    for process in psutil.process_iter():
        if 'constellation-node' == process.name() and \
                process.connections() and \
                process.connections()[0].laddr.port == int(port):

            print('Found {0} running with pid {1}'.format(process.name(), process.pid))

            return process

    return None


constellation_node_process = find_constellation_node()


if not constellation_node_process:
    raise Exception('Unable to find constellation running')

constellation_node_process.kill()

print('Shutting constellation')

os.chdir(curr_dir)

print('If constellation needs to be launched again, use this from constellation directory:')
print(cn.launch_cmd_line)

print('====== PASS =======')
