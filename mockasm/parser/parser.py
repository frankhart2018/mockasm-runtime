from mockasm.utils import error_utils
from ..utils import token_utils
from . import opcode
from mockasm import parser


class Parser:
    def __init__(self, tokens):
        self.__tokens = tokens
        self.__current_token_ptr = 0
        self.__opcodes = []
        
        self.__opcode_idx_to_label = {}
        self.__label_to_opcode_idx = {}

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

    def __bind_label_idx_to_jmps(self):
        for opcode_idx, label in self.__opcode_idx_to_label.items():
            if label not in self.__label_to_opcode_idx.keys():
                error_utils.error(msg=f"Cannot jump to unknown label '{label}'")

            self.__opcodes[opcode_idx].op_value = self.__label_to_opcode_idx[label]

    def __parse_mov(self, operator):
        # operator src, dst
        # operator -> mov/movzb
        # src -> $<number>|<register>|(<register>)|$_<number>
        # dst -> <register>|(<register>)|$_<number>
        expected_token_sequence = [operator, "number,register,location_at,address", "comma", "register,location_at,address"]

        value = ""
        register = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type] if type(expected_token_type) == str else expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if value == "" and current_token.token_type in ["number", "register", "location_at", "address"]:
                value = current_token.lexeme if current_token.token_type not in ["location_at", "address"] else "_" + current_token.lexeme
            elif current_token.token_type in ["number", "register", "location_at", "address"]:
                register = current_token.lexeme if current_token.token_type not in ["location_at", "address"] else "_" + current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        return opcode.OpCode(op_code=operator, op_value=value + "---" + register, line_num=line_num)

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

        return opcode.OpCode(op_code="ret", op_value="", line_num=current_token.line_num)

    def __parse_arithmetic_op(self, operator):
        # operator $<number>|<register>, <register>
        # operator -> add/sub
        expected_token_sequence = [operator, "number,register", "comma", "register"]

        value = ""
        register = ""
        line_num = 0
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

            line_num = current_token.line_num

        return opcode.OpCode(op_code=operator, op_value=value + "---" + register, line_num=line_num)

    def __parse_stack_op(self, operator):
        # operator $number|<register>
        # operator -> push/pop
        expected_token_sequence = [operator, "number,register"]

        value = ""
        line_num = 0
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

            line_num = current_token.line_num

        return opcode.OpCode(op_code=operator, op_value=value, line_num=line_num)

    def __parse_unary_op(self):
        # neg <register>
        expected_token_sequence = ["neg", "register"]

        register = ""
        line_num = 0
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

            line_num = current_token.line_num

        return opcode.OpCode(op_code="neg", op_value=register, line_num=line_num)

    def __parse_cmp(self):
        # cmp $<number>|<register>, <register>
        expected_token_sequence = ["cmp", "number,register", "comma", "register"]

        src_register = ""
        dest_register = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type] if type(expected_token_type) == str else expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if src_register == "" and current_token.token_type in ["number", "register"]:
                src_register = current_token.lexeme
            elif expected_token_type == "register":
                dest_register = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        return opcode.OpCode(op_code="cmp", op_value=src_register + "---" + dest_register, line_num=line_num)

    def __parse_set(self, operator):
        # operator $number|<register>
        # operator -> sete/setne/setl/setle
        expected_token_sequence = [operator, "number,register"]

        value = ""
        line_num = 0
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

            line_num = current_token.line_num

        return opcode.OpCode(op_code=operator, op_value=value, line_num=line_num)

    def __parse_lea(self):
        # lea <address>, <register>
        expected_token_sequence = ["lea", "address,global", "comma", "register"]

        address = ""
        register = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            if "," in expected_token_type:
                expected_token_type = expected_token_type.split(",")

            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type] if type(expected_token_type) == str else expected_token_type,
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type in ["address", "global"]:
                address = "_" + current_token.lexeme if current_token.token_type == "address" else current_token.lexeme
            elif expected_token_type == "register":
                register = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        return opcode.OpCode(op_code="lea", op_value=address + "---" + register, line_num=line_num)

    def __parse_jmp(self, operator):
        # operator <label>
        # operator -> jmp/je
        expected_token_sequence = [operator, "label"]

        label = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type == "label":
                label = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        # Will be used at the end of parsing for label idx binding
        self.__opcode_idx_to_label[len(self.__opcodes)] = label

        return opcode.OpCode(op_code=operator, op_value=label, line_num=line_num)

    def __parse_label(self):
        # label:
        expected_token_sequence = ["label", "colon"]

        label = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type == "label":
                label = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        # Will be used at the end of parsing for label idx binding
        self.__label_to_opcode_idx[label] = len(self.__opcodes)

        return opcode.OpCode(op_code="label", op_value=label, line_num=line_num)

    def __parse_call(self):
        # call <label>
        expected_token_sequence = ["call", "label"]

        label = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type == "label":
                label = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        # Will be used at the end of parsing for label idx binding
        self.__label_to_opcode_idx[label] = len(self.__opcodes)

        return opcode.OpCode(op_code="call", op_value=label, line_num=line_num)

    def __parse_global_var(self):
        # .global.<var-name>
        expected_token_sequence = ["global"]

        label = ""
        line_num = 0
        for expected_token_type in expected_token_sequence:
            current_token = self.__get_token_from_pos()
            token_utils.match_tokens(
                current_token_type=current_token.token_type,
                expected_token_types=[expected_token_type],
                error_msg=f"Expected '{expected_token_type}' got '{current_token.token_type}' at Line {current_token.line_num}",
            )

            if current_token.token_type == "global":
                label = current_token.lexeme

            self.__increment_token_ptr()

            line_num = current_token.line_num

        # Will be used at the end of parsing for label idx binding
        self.__label_to_opcode_idx[label] = len(self.__opcodes)

        return opcode.OpCode(op_code="global", op_value=label, line_num=line_num)

    def parse(self):
        while not self.__is_token_list_end():
            current_token = self.__get_token_from_pos()

            if current_token.token_type in ["mov", "movzb", "movsbq"]:
                current_opcode = self.__parse_mov(
                    operator=current_token.token_type
                )
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
                current_opcode = opcode.OpCode(op_code="cqo", op_value="", line_num=current_token.line_num)
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
            elif current_token.token_type == "cmp":
                current_opcode = self.__parse_cmp()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type in ["sete", "setne", "setl", "setle"]:
                current_opcode = self.__parse_set(
                    operator=current_token.token_type
                )
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "lea":
                current_opcode = self.__parse_lea()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type in ["jmp", "je"]:
                current_opcode = self.__parse_jmp(
                    operator=current_token.token_type
                )
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "label":
                current_opcode = self.__parse_label()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "call":
                current_opcode = self.__parse_call()
                self.__append_opcode(opcode=current_opcode)
            elif current_token.token_type == "global":
                current_opcode = self.__parse_global_var()
                self.__append_opcode(opcode=current_opcode)
            else:
                self.__increment_token_ptr()

        # Bind all the labels to correct jmp statements
        self.__bind_label_idx_to_jmps()

        return self.__opcodes
