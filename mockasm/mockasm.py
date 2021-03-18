import argparse

from .utils import file_utils


def run():
    parser = argparse.ArgumentParser(description="Mock ASM")
    parser.add_argument("--file_path", type="str", default="", help="Path to asm code")
    args = parser.parse_args()

    source_code = file_utils.read_file(path=args.file_path)

    print(source_code)