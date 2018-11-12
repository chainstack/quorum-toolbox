from . import templating


# discport is the discovery socket port. Disable it seems to be accepted practise. discovery happens on tcp anyway.
def make_enode_id_geth(enode, geth_address, geth_port):
    template_str = "enode://$enode@$geth_address:$geth_port?discport=0"
    kwds = {
        'enode': enode,
        'geth_address': geth_address,
        'geth_port': geth_port
    }

    return templating.template_substitute(template_str, kwds)


# $geth_ip is to be specified as IP only. Dns names are not accepted.
# https://github.com/ethereum/wiki/wiki/enode-url-format
def make_enode_id(enode, geth_address, geth_port, raft_port):
    enode_id_geth = make_enode_id_geth(enode, geth_address, geth_port)
    kwds = {
        'enode_id_geth': enode_id_geth,
        'raft_port': raft_port
    }

    template_str = "$enode_id_geth&raftport=$raft_port"

    return templating.template_substitute(template_str, kwds)


def make_enode_id2(enode_id_geth, raft_port):
    kwds = {
        'enode_id_geth': enode_id_geth,
        'raft_port': raft_port
    }

    template_str = "$enode_id_geth&raftport=$raft_port"

    return templating.template_substitute(template_str, kwds)