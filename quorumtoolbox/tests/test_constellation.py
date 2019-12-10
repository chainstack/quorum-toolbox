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

print('Created all artifacts and keys need for constellation node.')

print('====== PASS =======')
