def make_param(*args, joiner=" "):
    return joiner.join(str(elem) for elem in args)
