import argparse
from mockasm.lexer import token

from .utils import file_utils
from .lexer import lexer
from .parser import parser
from .runtime import vm

import copy
import json

def run():
    argparser = argparse.ArgumentParser(description="Mock ASM")
    argparser.add_argument("--file_path", type=str, default="", help="Path to asm code")
    argparser.add_argument(
        "--tokens", action="store_true", default=False, help="Show tokens"
    )
    argparser.add_argument(
        "--opcodes", action="store_true", default=False, help="Show opcodes"
    )
    argparser.add_argument(
        "--exec_opcodes", action="store_true", default=False, help="Show executed opcodes"
    )
    argparser.add_argument(
        "--exec_steps", action="store_true", default=False, help="Show execution steps"
    )
    args = argparser.parse_args()

    source_code = file_utils.read_file(path=args.file_path)

    lexer_obj = lexer.Lexer(source_code=source_code)
    tokens = lexer_obj.lexical_analyze()

    if args.tokens:
        print()
        print("*" * 50)
        print("Tokens")
        print("*" * 50)
        for token in tokens:
            print(token)

    parser_obj = parser.Parser(tokens=tokens)
    opcodes = parser_obj.parse()

    if args.opcodes:
        print()
        print("*" * 50)
        print("OpCodes")
        print("*" * 50)
        for opcode in opcodes:
            print(opcode)

    vm_obj = vm.VM(opcodes=opcodes)

    if args.tokens or args.opcodes:
        print()
        print("*" * 50)
        print("Output")
        print("*" * 50)

    if args.exec_steps:
        for sequence in vm_obj.execute(yield_execution=True):
            if(type(sequence) == dict):
                print("*" * 50)
                print(f"Line {sequence['line_num']}")
                print(f"Flags: {sequence['flags']}")
                print(f"Registers: {sequence['registers']}")
                print(f"Memory: {sequence['memory']}")
                print(f"Stack: {sequence['stack']}")
                print("*" * 50)
    else:
        _ = list(vm_obj.execute(show_exec_opcodes=args.exec_opcodes))
