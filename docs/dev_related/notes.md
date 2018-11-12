#Automated deployed of Quorum nodes via docker containers on Kubernetes


##Background
A Quorum node can logically be divided into the following components, with each component serving a specific role:
* Geth: The ethereum client, responsible for Ethereum related functionalities.

* Constelaltion/Tessera: Private transaction manager, responsible for privacy related functionalities, such as deploying and invoking private smart contrcats within the Quorum network. A Quorum network employs either of these two, meaning,  nodes within the network are all configured to use one or the other private transaction manager but never a mixture of both. A quorum node can be made to run without a private transaction manager, thereby ignoring all private transactions, by setting the PRIVATE_CONFIG to ignore during node start time. [See here](https://github.com/jpmorganchase/quorum/pull/462)
 
* Raft/IBFT: Consensus algorithm for the Quorum network, replaces the default POW/POS consensus algoritm of ethereum. A Quorum network employs either of these two, meaning,  nodes within the network are all configured to use one or the other consensus algorithm but never a mixture of both. Once a network has been launched with a specific consensus, the algorithm can't be changed.

###Automated Deployment (Work in progress)
Deployment scripts for Quorum have been written to reflect the components as listed above, with each component represented by a class:

```class Geth(context, url, rpcaddr, port=30303, rpcport=None)```
*context (string): A directory name or path. Geth related artifacts will be generated and stored in this location.*
*url (string): The public DNS/IP that this node will be assigned to.* ==NOTE: Currently only IP is supported.==
*rpcaddr (string): The IP address on which Geth JSON RPC will be served*
*port (integer, optional): The port Geth listens on. Defaults to 30303 by script.*
*rpcport (integer, optional): The port to serve JSON RPC on. Defaults to 8545 by Geth.*

```class Raft(context, enode_id, node_state, port=None, max_peers=None, block_time=None, peers=[])```
*context (string): A directory name or path. Raft related artifacts will be generated and stored in this location.*
*enode_id (string): The Enode Id for this node in the format "enode://$enode@$geth_ip:$geth_port?raftport=$raft_port"*
*node_state (string, ["initial", "new", "existing"]): The state of this node. "initial" represents a Quorum network that is being created for the first time that this node will become a part of. "new" represents a node that is being created newly to join an existing Quorum network. "existing" represents an existing node that is already part of a network.* ==NOTE: "existing is currently not supported"==.
*port (integer): The port for Raft to listen on. Defaults to 50303 by Raft.*
*max_peers (integer): The maximum number of raft peers in the network. Defaults to 25 by Raft.*
*block_time (integer): The interval at which new blocks are to be minted. Defaults to 50ms by Raft*
*peers (list): An address list of one or more Quorum nodes of a network this node is to join. Each address denotes the Geth JSON RPC serving endpoint of the respective node. Adress can be given as IP/DNS name. Or, a combination of IP/DNS and the RPC port.* 

```class Constellation(context, address, port=9000, other_nodes=[]```
*context (string): A directory name or path. Constellation related artifacts will be generated and stored in this location.*
*address (string): The public DNS/IP that this node will be assigned to.* ==NOTE: Currently only IP is supported.==
*port (integer):  The port for Raft to listen on. Defaults to 9000 by script.*
*other_nodes (list): An address list of one or more Quorum nodes of a network this node is to join. Each address denotes the constellation endpoint of the respective node. Each address has to be of format http://IP:PORT/ ==NOTE: Currently only IP is supported.==


###Tests


Clone Repo


#####Dependencies
* python 3.5^ and pip3
* See requirements.txt in main repo directory. Requirements can be installed as ```pip3 install -r requirements.txt```
* Install [constellation](https://github.com/jpmorganchase/constellation) (this will install the binary *constellation-node*)
* Install [geth](https://github.com/ethereum/go-ethereum/wiki/Installing-Geth) (this will install the binaries *geth* and *bootnode*)
* Tested on Ubuntu 16.04.4 LTS


**Constellation**
This test creates neccessary artifacts for a new Constellation component. Launches Constellation as a process using the artifacts, checks for the launched process and artifact consistency. Shutsdown the launched process on end.

1. In repo main directory, make a new copy of the template_dir. ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_constellation.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.

**Raft**
This test creates neccessary artifacts for a new Raft component. Checks for artifact consistency. Since Raft can't be launched on it own, this test does not attempt to launch Raft as a process.
1. In repo main directory, make a new copy of the template_dir. ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_raft.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.

**Geth**
This test creates neccessary artifacts for a new Geth component. Checks for artifact consistency. (TODO Launch Geth and check process)
1. In repo main directory, make a new copy of the template_dir. ```cp -r template_dir company1_q2_n0```. If company1_q2_n0 is already present, delete it first.
2. Run ```python3 test_geth.py```
3. Once test has completed successfully, do a diff of template_dir and company1_q2_n0 to find all the created artifacts.


###Containerization (Work in progress)
The component Quorum classes will be wrapped in a master class that will coordinate among the components to create a final Quorum node. Attributes of the node such as public IP, ports, consensus algorithm to use, PTM, initial/new/existing node etc. will be configured by the master class depending on inputs provided to the master class.

The created node will be compactly represented as a single directory. This directory will house keys, configurations, scripts, files/folders and other artifacts required to launch the Quorum node.

The containerization process is envisioned to be as simple as copying this folder into a base Quorum dokcer image, and setting the docker launch CMD to a script within this folder. The image can then be pushed to a cluster.





