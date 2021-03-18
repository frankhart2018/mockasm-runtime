from ..utils import error_utils


class VM:
    def __init__(self, opcodes):
        self.__opcodes = opcodes
        self.__current_opcode_ptr = 0

        self.__clear_registers()

    def __clear_registers(self):
        self.__registers = {"rax": None}

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

        value = int(value)
        self.__registers[register] = (
            self.__registers[register] + value
            if operator == "add"
            else self.__registers[register] - value
        )

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
            elif op_code.op_code in ["add", "sub"]:
                value, register = op_code.op_value.split("---")
                self.__execute_arithmetic_operation(
                    value=value, register=register, operator=op_code.op_code
                )
                self.__increment_opcode_ptr()