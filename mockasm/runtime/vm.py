from ..utils import error_utils


class VM:
    def __init__(self, opcodes):
        self.__opcodes = opcodes
        self.__current_opcode_ptr = 0

        self.__clear_registers()

    def __clear_registers(self):
        self.__registers = {
            "rax": None,
            "rdi": None,
            "al": None,
        }

        self.__stack = []

        self.__flags = {
            "zero": 0,
            "negative": 0,
            "positive": 0,
        }

    def __increment_opcode_ptr(self):
        self.__current_opcode_ptr += 1

    def __is_opcode_list_end(self):
        return self.__current_opcode_ptr >= len(self.__opcodes)

    def __get_opcode_from_pos(self, pos=None):
        return (
            self.__opcodes[self.__current_opcode_ptr]
            if pos == None
            else self.__opcodes[pos]
        )

    def __parse_value(self, value, error_msg):
        old_value = value
        value = int(value) if value not in self.__registers.keys() else self.__registers.get(value, 0)

        if value == None:
            error_utils.error(msg=error_msg.replace("{}", old_value))

        return value

    def __execute_push_to_stack(self, value):
        value = self.__parse_value(
            value=value,
            error_msg="Register '{}' has not been set, you cannot push it to stack"
        )

        self.__stack.append(value)

    def __execute_pop_from_stack(self, register):
        value = self.__stack.pop()
        self.__registers[register] = int(value)

    def __execute_move_instruction(self, value, register):
        value = self.__parse_value(
            value=value,
            error_msg="Register '{}' has not been set, you cannot move it to '" + register + "'"
        )

        self.__registers[register] = value

    def __execute_return_instruction(self):
        for value in self.__registers.values():
            if value != None:
                print(value)
                break

    def __execute_arithmetic_operation(self, value, register, operator):
        if self.__registers[register] == None:
            error_utils.error(
                msg=f"Register {register} does not have any value, set a value to perform arithmetic operation"
            )

        value = self.__parse_value(
            value=value,
            error_msg="Register {} has not been set, you cannot perform " + operator + " operation"
        )

        new_value = 0
        existing_reg_value = self.__registers[register]
        if operator == "add":
            new_value = existing_reg_value + value
        elif operator == "sub":
            new_value = existing_reg_value - value
        elif operator == "imul":
            new_value = existing_reg_value * value
        elif operator == "idiv":
            new_value = existing_reg_value // value

        self.__registers[register] = new_value

    def __execute_unary_operation(self, register):
        if self.__registers[register] == None:
            error_utils.error(msg=f"Register '{register}' has not been set, cannot negate empty value")

        self.__registers[register] *= -1

    def __execute_compare(self, src_register, dst_register):
        src_value = self.__parse_value(
            value=src_register,
            error_msg="Register '{}' has not been set, cannot use it in cmp"
        )

        dst_value = self.__parse_value(
            value=dst_register,
            error_msg="Register '{}' has not been set, cannot use it in cmp"
        )

        comparison_result = dst_value - src_value

        if comparison_result < 0:
            self.__flags["negative"] = 1
        elif comparison_result == 0:
            self.__flags["zero"] = 1
        elif comparison_result > 0:
            self.__flags["positive"] = 1

    def __execute_comparison_op(self, operator, register):
        zero_flag_val = self.__flags["zero"]
        negative_flag_val = self.__flags["negative"]
        positive_flag_val = self.__flags["positive"]

        if operator == "sete":
            if zero_flag_val == 1:
                self.__registers[register] = 1
            elif zero_flag_val == 0:
                self.__registers[register] = 0

            self.__flags["zero"] = 0 
        elif operator == "setne":
            if zero_flag_val == 1:
                self.__registers[register] = 0
            elif zero_flag_val == 0:
                self.__registers[register] = 1

            self.__flags["zero"] = 0
        elif operator == "setl":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__registers[register] = 1
            else:
                self.__registers[register] = 0

            self.__flags["negative"] = 0
            self.__flags["positive"] = 0
        elif operator == "setle":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__registers[register] = 1
            elif zero_flag_val == 1:
                self.__registers[register] = 1
            else:
                self.__registers[register] = 0

            self.__flags["negative"] = 0
            self.__flags["positive"] = 0
            self.__flags["zero"] = 0

    def execute(self):
        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if op_code.op_code in ["mov", "movzb"]:
                value, register = op_code.op_value.split("---")
                self.__execute_move_instruction(value=value, register=register)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "ret":
                self.__execute_return_instruction()
                self.__increment_opcode_ptr()
            elif op_code.op_code in ["add", "sub", "imul", "idiv"]:
                value, register = op_code.op_value.split("---")
                self.__execute_arithmetic_operation(
                    value=value, register=register, operator=op_code.op_code
                )
                self.__increment_opcode_ptr()
            elif op_code.op_code == "cqo":
                self.__increment_opcode_ptr()
            elif op_code.op_code == "neg":
                self.__execute_unary_operation(register=op_code.op_value)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "push":
                self.__execute_push_to_stack(value=op_code.op_value)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "pop":
                self.__execute_pop_from_stack(register=op_code.op_value)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "cmp":
                src_register, dst_register = op_code.op_value.split("---")
                self.__execute_compare(
                    src_register=src_register,
                    dst_register=dst_register
                )
                self.__increment_opcode_ptr()
            elif op_code.op_code in ["sete", "setne", "setl", "setle"]:
                self.__execute_comparison_op(
                    operator=op_code.op_code,
                    register=op_code.op_value
                )
                self.__increment_opcode_ptr()
