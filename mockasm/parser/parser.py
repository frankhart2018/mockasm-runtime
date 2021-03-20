from ..utils import token_utils
from . import opcode


class Parser:
    def __init__(self, tokens):
        self.__tokens = tokens
        self.__current_token_ptr = 0
        self.__opcodes = []

    def __is_token_list_end(self):
        return self.__current_token_ptr >= len(self.__tokens)

    def __get_token_from_pos(self, pos=None):
        return (
            self.__tokens[self.__current_token_ptr]
            if pos == None
            else self.__tokens[pos]
        )

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
            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if expected_token_type == "number":
                value = current_token.lexeme
            elif expected_token_type == "register":
                register = current_token.lexeme

            self.__increment_token_ptr()

        return opcode.OpCode(op_code="mov", op_value=value + "---" + register)

    def __parse_ret(self):
        # ret
        current_token = self.__get_token_from_pos()
        expected_token_type = "ret"
        token_utils.match_tokens(
            current_token_type=current_token.token_type,
            expected_token_types=[expected_token_type],
            error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
        )

        self.__increment_token_ptr()

        return opcode.OpCode(op_code="ret", op_value="")

    def __parse_arithmetic_op(self, operator):
        # operator $<number>|<register>, <register>
        # operator -> add/sub
        expected_token_sequence = [operator, "number,register", "comma", "register"]

        value = ""
        register = ""
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type] if type(expected_token_type) == str else expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if value == "" and (current_token.token_type == "number" or current_token.token_type == "register"):
                value = current_token.lexeme
            elif expected_token_type == "register":
                register = current_token.lexeme

            self.__increment_token_ptr()

        return opcode.OpCode(op_code=operator, op_value=value + "---" + register)

    def __parse_stack_op(self, operator):
        # operator $number|<register>
        # operator -> push/pop
        expected_token_sequence = [operator, "number,register"]

        value = ""
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type] if type(expected_token_type) == str else expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if value == "" and (current_token.token_type == "number" or current_token.token_type == "register"):
                value = current_token.lexeme

            self.__increment_token_ptr()

        return opcode.OpCode(op_code=operator, op_value=value)

    def __parse_unary_op(self):
        # neg <register>
        expected_token_sequence = ["neg", "register"]

        register = ""
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type == "register":
                register = current_token.lexeme

            self.__increment_token_ptr()

        return opcode.OpCode(op_code="neg", op_value=register)

    def parse(self):
        while not self.__is_token_list_end():
            current_token = self.__get_token_from_pos()

            if current_token.token_type == "mov":
                current_opcode = self.__parse_mov()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "ret":
                current_opcode = self.__parse_ret()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type in ["add", "sub", "imul", "idiv"]:
                current_opcode = self.__parse_arithmetic_op(
                    operator=current_token.token_type
                )
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "cqo":
                current_opcode = opcode.OpCode(op_code="cqo", op_value="")
                self.__append_opcode(opcode=current_opcode)
                self.__increment_token_ptr()
            elif current_token.token_type == "neg":
                current_opcode = self.__parse_unary_op()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type in ["push", "pop"]:
                current_opcode = self.__parse_stack_op(
                    operator=current_token.token_type
                )
                self.__append_opcode(opcode=current_opcode)
            else:
                self.__increment_token_ptr()

        return self.__opcodes
