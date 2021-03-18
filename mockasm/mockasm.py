import argparse
from mockasm.lexer import token

from .utils import file_utils
from .lexer import lexer
from .parser import parser


def run():
    argparser = argparse.ArgumentParser(description="Mock ASM")
    argparser.add_argument("--file_path", type=str, default="", help="Path to asm code")
    args = argparser.parse_args()

    source_code = file_utils.read_file(path=args.file_path)

    lexer_obj = lexer.Lexer(source_code=source_code)
    tokens = lexer_obj.lexical_analyze()

    parser_obj = parser.Parser(tokens=tokens)
    opcodes = parser_obj.parse()

    for opcode in opcodes:
        print(opcode)