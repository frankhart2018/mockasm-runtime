def read_file(path):
    if path == "":
        raise ValueError("\033[91mFile path cannot be empty while reading a file!\033[m")

    with open(path, "r") as file:
        file_contents = file.read()

    return file_contents