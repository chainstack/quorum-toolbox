import os
from shutil import rmtree, copytree, copy2


def make_full_path(path, name):
    return os.path.join(path, name)


def make_dir(dir_to_create, where=""):
    """
    Create new directory, recursively creating parent directories as needed.

    If leaf directory already exists, exception raised.

    :param dir_to_create: Name of directory to create (e.g. my_dir or my_dirs/my_dir).
    :param where: Optional. If given, dir_to_create is created in given location (e.g. /home/user).
    If not, dir_to_create is created in current working directory.
    :return: None.
    """

    dir_to_create = make_full_path(where, dir_to_create)
    os.makedirs(dir_to_create)


def del_dir(dir_to_delete, where=""):
    """
    Delete directory, recursively all files and directories within are also deleted.

    If directory to be deleted is not present, exception raised.

    :param dir_to_delete: Name of directory to be deleted (e.g. my_dir or my_dirs/my_dir).
    :param where: Optional. If given, dir_to_delete is deleted in given location (e.g..... /home/user).
    If not, dir_to_delete is deleted from current working directory.
    :return: None
    """
    dir_to_delete = make_full_path(where, dir_to_delete)
    rmtree(dir_to_delete)


def copy_dir(dir_to_copy, dst, src=""):
    """
    Copy directory, recursively copy all contents within and recursively create destination path as needed.

    If destination directory already present, exception raised.

    :param dir_to_copy: Name of directory to be copied (e.g. my_dir or my_dirs/my_dir)
    :param dst: Location to copy to (e.g. /home/user/my_dir or /home/user/my_dir_rename)
    :param src: Optional. Location from which to copy (e.g. /home).
    If not given, current working directory is used.
    :return: None
    """
    dir_to_copy = make_full_path(src, dir_to_copy)
    copytree(dir_to_copy, dst)


def copy_file(file_to_copy, dst, src=""):
    """
    Copy file including permissions and metadata.

    If destination path does not exist, exception raised.

    :param file_to_copy: Name of file to be copied (e.g. my_file.txt or my_dir/my_file.txt).
    :param dst: Location to copy to (e.g. /home/user or /home/user/file_rename.txt).
    :param src: Optional. Location from which to copy (e.g. /home/temp).
    If not given, current working directory is used.
    :return: None
    """
    file_to_copy = make_full_path(src, file_to_copy)
    copy2(file_to_copy, dst)


def copy_files_ext(ext_to_copy, dst, src=""):
    """
    Copy files of particular extension. Files only from the parent level are copied, not recursive.

    Uses copy_file.

    :param ext_to_copy: The file extension to look for (e.g. .txt)
    :param dst:  The location to copy files into (e.g. /home/user)
    :param src: Optional. Location from which to copy (e.g. /home/temp)
    If not given, current working directory is used.
    :return: None
    """
    if src == "":
        contents = os.listdir(".")
    else:
        contents = os.listdir(src)

    for elem in contents:
        if elem.endswith(ext_to_copy):
            copy_file(elem, dst, src=src)


def is_a_file(file_to_check, src=""):
    file_to_check = make_full_path(src, file_to_check)
    return os.path.isfile(file_to_check)


def read_file(file_name, src=""):
    with open(make_full_path(src, file_name), "r") as fp:
        result = fp.read()

    return result


def write_file(file_name, content, src=""):
    with open(make_full_path(src, file_name), "w") as fp:
        fp.write(content)


def change_file_permissions(file_name, new_permission, src=""):
    file_name = make_full_path(src, file_name)


# caution: will change wd for all threads!, making process thread unsafe.
def change_wrk_directory(new_dir):
    curr_dir = os.path.abspath(os.curdir)
    os.chdir(new_dir)

    return curr_dir
