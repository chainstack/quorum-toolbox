from string import Template

from . import fs_utils


def template_substitute(template, kwds, write=True):
    """
    String template substitution either from file or string.

    :param template: File name or string template literal. For file, the content of the file is treated
    as the template.
    :param kwds: A dictionary of key-value substitutions
    :param write: If True, write template file after substitution
    :return: The replaced string result. When template is a file, the contents of the file is overwritten
    with the replaced string result.
    """

    is_file = fs_utils.is_a_file(template)

    if is_file:
        template_str = fs_utils.read_file(template)
    else:
        template_str = template

    t = Template(template_str)
    t = t.safe_substitute(kwds)

    if is_file and write:
        fs_utils.write_file(template, t)

    return t
