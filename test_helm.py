import json
import shutil
import sys
import os
from time import sleep
from collections import namedtuple

import requests
import sh
from create_quorum_node import CreateQuorumNode


deploy_node_params = namedtuple('deploy_node_params', [
    'helm_node_charts',
    'selector',
    'artifacts_dir',
    'network_id',
    'constellation_url',
    'join_id',
    'constellation_peer_url'
])


# ------------------------------------------- check dependencies ----------------------------
def check_requisites():
    binaries = ["constellation-node", "geth", "helm", "kubectl"]

    dependencies = []
    for binary in binaries:
        dependencies.append(sh.Command("which").bake(binary))

    for index, dependency in enumerate(dependencies):
        run_cmd(dependency, "Dependency failed. {0} binary not found. See [link].".format(binaries[index]))

    if len(sys.argv) != 4:
        print("Wrong number of parameters, need 3. \
(e.g. python3 test_helm.py path/to/service/charts /path/to/node/charts number_of_nodes_to_launch")
        exit()


# ------------------------------------------- run bash cmd -----------------------------------
def run_cmd(cmd, error):
    try:
        result = cmd()
    except sh.ErrorReturnCode as e:
        print(error, "Exit code: {0}, Stdout: {1}, Stderr: {2}."
              .format(e.exit_code, e.stdout.decode(sh.DEFAULT_ENCODING), e.stderr.decode(sh.DEFAULT_ENCODING)))
        exit()
    else:
        return result  # .stdout.decode(sh.DEFAULT_ENCODING)


# ------------------------------------------- get ext ip from k8 service --------------------
def get_ext_ip(service_name):
    cmd = sh.Command("kubectl").bake("get", "service")
    while True:
        print("Waiting for K8 ext ip in service {0} (this may take few minutes)".format(service_name))
        result = run_cmd(cmd, "Error in kubectl get services")
        ext_ip = [line.split()[3] for line in result if service_name in line][0]
        if "pending" in ext_ip:
            sleep(60)
        else:
            return ext_ip


# ------------------------------------------- create helm service -----------------------------------
def helm_deploy_service(helm_service_charts, selector):
    cmd = sh.Command("/bin/bash").bake(os.path.join(helm_service_charts, "deploy.sh"), selector,
                                       _cwd=helm_service_charts)
    result = run_cmd(cmd, "Error creating helm service.")
    service_name = release_name(result) + "-service"
    ext_ip = get_ext_ip(service_name)

    print("Created service {0} with ext ip {1}".format(service_name, ext_ip))

    return ext_ip


# ------------------------------------------- get pod name from k8 ---------------------------------
def get_pod_name(deployment_name):
    cmd = sh.Command("kubectl").bake("get", "pods")
    sleep(10)

    print("Looking for pod name in deployment {0}".format(deployment_name))
    result = run_cmd(cmd, "Error in kubectl get pods")

    pod_name = ""
    pod_status = ""

    for line in result:
        if deployment_name in line:
            arr = line.split()
            pod_name = arr[0]
            pod_status = arr[2]

    if "Running" != pod_status:
        print("Error: Pod {0} not in running state".format(pod_name))
        exit()

    return pod_name


# ------------------------------------------- create helm initial node deployment ----------------
def helm_deploy_initial_node(params):
    cmd = sh.Command("/bin/bash").bake(os.path.join(params.helm_node_charts, "deploy.sh"),
                                       0,
                                       params.selector,
                                       params.artifacts_dir,
                                       params.network_id,
                                       params.constellation_url,
                                       _cwd=params.helm_node_charts
                                       )

    helm_deploy_node(cmd)

    return


# ------------------------------------------- create helm new node deployment -----------------------
def helm_deploy_new_node(params):
    cmd = sh.Command("/bin/bash").bake(os.path.join(params.helm_node_charts, "deploy.sh"),
                                       1,
                                       params.selector,
                                       params.artifacts_dir,
                                       params.network_id,
                                       params.constellation_url,
                                       params.join_id,
                                       params.constellation_peer_url,
                                       _cwd=params.helm_node_charts)

    helm_deploy_node(cmd)

    return


# -------------------------------------------- create helm node --------------------------------------
def helm_deploy_node(cmd):
    result = run_cmd(cmd, "Error creating helm node.")
    deployment_name = release_name(result) + "-quorum-node-"
    pod_name = get_pod_name(deployment_name)

    print("Created quorum node in pod {0}".format(pod_name))

    return


# ---------------------------------------- get helm release name -----------------------------------
def release_name(result):
    return [line.split()[1] for line in result if "NAME:" in line][0]


# ----------------------------------------- rm dir -------------------------------------------------
def rm_dir(dir_name):
    try:
        shutil.rmtree(dir_name)
    except Exception:
        pass


# --------------------------------------------------------------------------------------------------
check_requisites()

helm_service_charts = sys.argv[1]
helm_node_charts = sys.argv[2]
target_number_of_nodes = 5 if int(sys.argv[3]) > 5 else int(sys.argv[3])

print("-----------------------------------------------------------------------")
print("Will deploy maximum {0} number of quorum nodes".format(target_number_of_nodes))
this_cmd = sh.Command("kubectl").bake("config", "current-context")
this_result = run_cmd(this_cmd, "Error running kubectl config current-context")
print("The current kubectl context for deployment: {0}".format(this_result))
print("Quorum service charts: {0}".format(helm_service_charts))
print("Quorum node deployment charts: {0}".format(helm_node_charts))

this_cmd = sh.Command("helm").bake("version")
this_result = run_cmd(this_cmd, "Error looking for helm and tiller. Are they installed and running?")
print("\nHelm and Tiller: {0}".format(this_result))
print("-----------------------------------------------------------------------")

inp = input("Enter 0 to quit now, anything else to start deployment: ")

if inp == "0":
    print("Quiting w.o any changes")
    exit()

# ------------------------------- start to deploy nodes ---------------------------------
number_of_nodes = 0
node_name = "acme_corp_node{0}".format(number_of_nodes)

# get ext IP address for initial node
print("\n------------------- Creating Service for node {0} ------------------------".format(number_of_nodes))
ext_ip_initial = helm_deploy_service(helm_service_charts, node_name)

context = node_name
address = ext_ip_initial

# remove artifacts folder if already present
rm_dir(context)

print("------------------- Creating Artifacts for node {0} ------------------------".format(number_of_nodes))

# create artifacts for initial node
node_params = {
    'context': context,
    'address': address,
    'node_state': "initial"
}

qn = CreateQuorumNode(node_params)

print("Created artifacts in folder: {0}. For your info: 1. Network id: {1} 2. Constellation Url: {2}"
      .format(context, qn.networkid, qn.ptm_url))

networkid = qn.networkid
genesis_content = qn.genesis_content

constellation_url = qn.ptm_url
artifacts_dir = os.path.join(os.getcwd(), context)

print("------------------- Creating Pod for node {0} ------------------------".format(number_of_nodes))

# deploy the initial node
deploy_params = deploy_node_params(helm_node_charts,
                                   node_name,
                                   artifacts_dir,
                                   networkid,
                                   constellation_url,
                                   0,
                                   ""
                                   )

helm_deploy_initial_node(deploy_params)
number_of_nodes += 1

while True:
    node_name = "acme_corp_node{0}".format(number_of_nodes)
    print("\n------------------- Creating Service for node {0} ------------------------".format(number_of_nodes))
    ext_ip_new = helm_deploy_service(helm_service_charts, node_name)

    context = node_name
    new_address = ext_ip_new

    rm_dir(context)

    print("------------------- Creating Artifacts for node {0} ------------------------".format(number_of_nodes))
    # create artifacts for new nodes
    node_params = {
        'context': context,
        'address': new_address,
        'node_state': "new",
        'networkid': networkid
    }

    network_params = {
        'genesis_content': genesis_content,
        'other_raft_public_ip': ext_ip_initial,
        'other_constellation_public_ip': ext_ip_initial
    }

    qn = CreateQuorumNode(node_params, network_params)

    print("\nCreated artifacts for new node")
    print("Created artifacts in folder: {0}. For your info: 1. Join id: {1} 2. Constellation Url: {2} \
3. Constellation peer url: {3}".format(context, qn.consensus_id, qn.ptm_url, qn.ptm_peers))

    artifacts_dir = os.path.join(os.getcwd(), context)
    constellation_url = qn.ptm_url
    join_id = qn.consensus_id
    constellation_peer_url = qn.ptm_peers

    print("------------------- Creating Pod for node {0} ------------------------".format(number_of_nodes))

    deploy_params = deploy_node_params(helm_node_charts,
                                       node_name,
                                       artifacts_dir,
                                       networkid,
                                       constellation_url,
                                       join_id,
                                       constellation_peer_url
                                       )

    helm_deploy_new_node(deploy_params)
    number_of_nodes += 1

    if number_of_nodes == target_number_of_nodes:
        break

print("------------------- ------------------------ ------------------------")

# ----------------------------------------------------------------------------------------------------

print("{0} quorum nodes deployed. Checking RPC....".format(target_number_of_nodes))
sleep(60)  # give some time for all nodes to sync

body = {
    'jsonrpc': "2.0",
    'method': "net_peerCount",
    'params': [],
    'id': 74
}

ext_ip_initial = 'http://' + ext_ip_initial + ':8545'

result = ""
try:
    result = requests.post(ext_ip_initial, data=json.dumps(body))
except Exception as e:
    print("Error while making RPC call ", e)
    exit()

peer_count = int(json.loads(result.text)['result'], 16) + 1

if peer_count != target_number_of_nodes:
    print("Error: Peer count {0} does not match target number of nodes {1}".format(peer_count, target_number_of_nodes))
    exit()

print("Found number of peers via RPC: {0}".format(peer_count))
print("------------------------------------------------------------------------")

this_cmd = sh.Command("helm").bake("list")
this_result = run_cmd(this_cmd, "Error when running helm list")
print("The following helm services are active. Delete when not using.")
print(this_result)

print("Bye")
# ----------------------------------------------------------------------------------------------
