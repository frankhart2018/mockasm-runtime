from . import error_utils

def read_file(path):
    if path == "":
        error_utils.error(msg="File path cannot be empty while reading a file!")

    with open(path, "r") as file:
        file_contents = file.read()

    return file_contents