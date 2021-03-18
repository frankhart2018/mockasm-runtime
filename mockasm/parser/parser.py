from ..utils import token_utils
from . import opcode

class Parser:
    def __init__(self, tokens):
        self.__tokens = tokens
        self.__current_token_ptr = 0
        self.__opcodes = []

    def __is_token_list_end(self):
        return self.__current_token_ptr >= len(self.__tokens)

    def __get_current_token(self, pos=None):
        return self.__tokens[self.__current_token_ptr] if pos == None else self.__tokens[pos]

    def __append_opcode(self, opcode):
        self.__opcodes.append(opcode)

    def __increment_token_ptr(self, by=None):
        self.__current_token_ptr += 1 if by == None else by

    def __parse_mov(self):
        # mov $<number>, <register>
        expected_token_sequence = ["mov", "number", "comma", "register"]

        value = ""
        register = ""
        for expected_token_type in expected_token_sequence:
            current_token = self.__get_current_token()
            token_utils.match_tokens(
                current_token_type=current_token.token_type, 
                expected_token_type=expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}"
            )

            if expected_token_type == "number":
                value = current_token.lexeme
            elif expected_token_type == "register":
                register = current_token.lexeme

            self.__increment_token_ptr()

        return opcode.OpCode(op_code="mov", op_value=value + "---" + register)

    def parse(self):
        while not self.__is_token_list_end():
           current_token = self.__get_current_token()

           if current_token.token_type == "mov":
               current_opcode = self.__parse_mov()
               self.__append_opcode(opcode=current_opcode)
               self.__increment_token_ptr()
           else:
               self.__increment_token_ptr()

        return self.__opcodes