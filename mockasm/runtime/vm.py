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
        }

        self.__stack = []

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
        self.__registers[register] = int(value)

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

    def execute(self):
        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if op_code.op_code == "mov":
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
