import argparse

from .utils import file_utils
from .lexer import lexer


def run():
    parser = argparse.ArgumentParser(description="Mock ASM")
    parser.add_argument("--file_path", type=str, default="", help="Path to asm code")
    args = parser.parse_args()

    source_code = file_utils.read_file(path=args.file_path)

    lexer_obj = lexer.Lexer(source_code=source_code)
    tokens = lexer_obj.lexical_analyze()

    for token in tokens:
        print(token)