def make_node_param(*args, joiner=" "):
    return joiner.join(str(elem) for elem in args)


def is_istanbul_node(node_state):
    return node_state == 'new_ibft' or node_state == 'initial_ibft'


def is_raft_node(node_state):
    return node_state == 'new' or node_state == 'initial'


def is_raft_or_istanbul_node(node_state):
    return is_raft_node(node_state) or is_istanbul_node(node_state)


def is_initial_node(node_state):
    return node_state == 'initial' or node_state == 'initial_ibft'


def is_new_node(node_state):
    return node_state == 'new' or node_state == 'new_ibft'