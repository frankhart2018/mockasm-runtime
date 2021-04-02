from mockasm.parser import opcode
from ..utils import error_utils


class VM:
    def __init__(self, opcodes):
        self.__opcodes = opcodes
        self.__current_opcode_ptr = 0

        self.__clear_registers()

    def __clear_flags(self):
        self.__flags = {
            "zero": 0,
            "negative": 0,
            "positive": 0,
        }

    def __clear_registers(self):
        self.__registers = {
            "rax": None,
            "rdi": None,
            "rsi": None,
            "rdx": None,
            "rcx": None,
            "al": None,
            "r8": None,
            "r9": None,
            "rsp": 0,
            "rbp": 0,
        }

        self.__clear_flags()

        self.__stack = []
        self.__memory = {}
        self.__call_stack = []

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

    def __find_opcode_idx(self, op):
        for i, opcode in enumerate(self.__opcodes):
            if op == opcode:
                return i

        return None

    def __parse_value(self, value, error_msg):
        old_value = value
        
        if not value.startswith("_") and value not in self.__registers.keys():
            value = int(value)
        else:
            if value.startswith("_"):
                if(value[1:].isdigit()):
                    value = self.__read_from_memory(mem_location=value)
                else:
                    value = self.__read_from_memory(mem_location=self.__registers[value[1:]])
            else:
                value = self.__registers[value]

        if value == None:
            error_utils.error(msg=error_msg.replace("{}", old_value))

        return value

    def __execute_push_to_stack(self, value):
        value = self.__parse_value(
            value=value,
            error_msg="Register '{}' has not been set, you cannot push it to stack"
        )

        self.__stack.append(value)

        self.__registers["rsp"] += 8

    def __execute_pop_from_stack(self, register):
        value = self.__stack.pop()
        self.__registers[register] = int(value) if type(value) != int and not value.startswith("_") and not value.startswith("g_") else value

        self.__registers["rsp"] -= 8

    def __compute_true_mem_loc(self, mem_location):
        if type(mem_location) == int:
            return mem_location

        mem_location = -1 * int(mem_location[1:]) + self.__registers["rbp"] if mem_location[1:].isdigit() and mem_location[0] == "_" else mem_location
        return int(mem_location) if type(mem_location) == str and mem_location.isdigit() else mem_location

    def __store_in_memory(self, mem_location, value):
        mem_location = self.__compute_true_mem_loc(mem_location)
        self.__memory[mem_location] = value

    def __read_from_memory(self, mem_location):
        mem_location = self.__compute_true_mem_loc(mem_location)
        return self.__memory.get(mem_location, None)

    def __execute_move_instruction(self, value, register):
        value = self.__parse_value(
            value=value,
            error_msg="Register '{}' has not been set, you cannot move it to '" + register + "'"
        )
        
        if register.startswith("_"):
            if(register[1:].isdigit()):
                self.__store_in_memory(mem_location=register, value=value)
            else:
                self.__store_in_memory(mem_location=self.__registers[register[1:]], value=value)
        else:
            self.__registers[register] = value

    def __execute_return_instruction(self):
        if len(self.__call_stack) == 0:
            for value in self.__registers.values():
                if value != None:
                    if type(value) == str:
                        value = value.replace("_", "")
                        value = abs(int(value))
                    print(value)
                    break
            return True
        else:
            self.__current_opcode_ptr = self.__call_stack.pop()
            return False

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

        if type(existing_reg_value) == str and existing_reg_value.startswith("g_"):
            existing_reg_value = self.__read_from_memory(mem_location=existing_reg_value)

        if type(value) == str and value.startswith("_"):
            value = -1 * int(value[1:])

        register_is_mem_loc = False
        if type(existing_reg_value) == str and existing_reg_value.startswith("_"):
            existing_reg_value = -1 * int(existing_reg_value[1:])
            register_is_mem_loc = True

        if operator == "add":
            new_value = existing_reg_value + value
        elif operator == "sub":
            new_value = existing_reg_value - value
        elif operator == "imul":
            new_value = existing_reg_value * value
        elif operator == "idiv":
            new_value = existing_reg_value // value

        self.__registers[register] = new_value if not register_is_mem_loc else "_" + str(-1 * new_value)

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
        elif operator == "setne":
            if zero_flag_val == 1:
                self.__registers[register] = 0
            elif zero_flag_val == 0:
                self.__registers[register] = 1
        elif operator == "setl":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__registers[register] = 1
            else:
                self.__registers[register] = 0
        elif operator == "setle":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__registers[register] = 1
            elif zero_flag_val == 1:
                self.__registers[register] = 1
            else:
                self.__registers[register] = 0

        self.__clear_flags()

    def __execute_lea(self, address, register):
        self.__registers[register] = self.__compute_true_mem_loc(address)

    def __execute_jmp(self, jmp_idx):
        self.__current_opcode_ptr = jmp_idx

    def __execute_conditional_jump(self, jmp_idx, on):
        if self.__flags[on]:
            self.__current_opcode_ptr = jmp_idx

        self.__clear_flags()

    def __execute_call(self, label):
        label_opcode = opcode.OpCode(op_code="label", op_value=label.split(".")[-1], line_num=1)
        label_opcode_idx = None

        label_opcode_idx = self.__find_opcode_idx(op=label_opcode)

        if label_opcode_idx == None:
            error_utils.error(msg=f"Label .L.{label} not found, but used in call statement")

        self.__call_stack.append(self.__current_opcode_ptr)
        self.__current_opcode_ptr = label_opcode_idx

    def __execute_global_var(self, global_var_name):
        self.__store_in_memory(mem_location=global_var_name, value=0)

    def execute(self, yield_execution=False):
        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if op_code.op_code == "global":
                global_var_name = op_code.op_value
                self.__execute_global_var(global_var_name=global_var_name)
                self.__increment_opcode_ptr()
            else:
                break

        main_opcode = opcode.OpCode(op_code="label", op_value="main", line_num=1)
        main_opcode_idx = self.__find_opcode_idx(op=main_opcode)

        if main_opcode_idx != None:
            self.__current_opcode_ptr = main_opcode_idx

        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if op_code.op_code in ["mov", "movzb"]:
                value, register = op_code.op_value.split("---")
                self.__execute_move_instruction(value=value, register=register)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "ret":
                is_end = self.__execute_return_instruction()
                
                if is_end:
                    break

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
            elif op_code.op_code == "lea":
                address, register = op_code.op_value.split("---")
                self.__execute_lea(
                    address=address,
                    register=register
                )
                self.__increment_opcode_ptr()
            elif op_code.op_code == "jmp":
                jmp_idx = int(op_code.op_value)
                self.__execute_jmp(jmp_idx=jmp_idx)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "je":
                jmp_idx = int(op_code.op_value)
                self.__execute_conditional_jump(jmp_idx=jmp_idx, on="zero")
                self.__increment_opcode_ptr()
            elif op_code.op_code == "label":
                self.__increment_opcode_ptr()
            elif op_code.op_code == "call":
                label = op_code.op_value
                self.__execute_call(label=label)
                self.__increment_opcode_ptr()

            if yield_execution:
                executed_opcode = self.__opcodes[self.__current_opcode_ptr - 1]

                yield {
                    "line_num": executed_opcode.line_num,
                    "flags": self.__flags,
                    "registers": self.__registers,
                    "memory": self.__memory,
                    "stack": self.__stack,
                }

        if yield_execution:
            yield self.__registers["rax"]
        else:
            return self.__registers["rax"]