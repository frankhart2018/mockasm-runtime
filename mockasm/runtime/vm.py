import collections

from mockasm.parser import opcode
from ..utils import error_utils


class VM:
    def __init__(self, opcodes):
        self.__opcodes = opcodes
        self.__current_opcode_ptr = 0
        self.__register_tuple = collections.namedtuple("register", ["value", "num_bytes"])

        self.__clear_registers()

    def __clear_flags(self):
        self.__flags = {
            "zero": 0,
            "negative": 0,
            "positive": 0,
        }

    def __clear_registers(self):
        self.__registers = {
            "rax": self.__register_tuple(value=None, num_bytes=64),

            "rdi": self.__register_tuple(value=None, num_bytes=64),
            "rsi": self.__register_tuple(value=None, num_bytes=64),
            "rdx": self.__register_tuple(value=None, num_bytes=64),
            "rcx": self.__register_tuple(value=None, num_bytes=64),
            "r8": self.__register_tuple(value=None, num_bytes=64),
            "r9": self.__register_tuple(value=None, num_bytes=64),

            "rsp": self.__register_tuple(value=0, num_bytes=64),
            "rbp": self.__register_tuple(value=0, num_bytes=64),

            "edi": self.__register_tuple(value=None, num_bytes=32),
            "esi": self.__register_tuple(value=None, num_bytes=32),
            "edx": self.__register_tuple(value=None, num_bytes=32),
            "ecx": self.__register_tuple(value=None, num_bytes=32),
            "r8d": self.__register_tuple(value=None, num_bytes=32),
            "r9d": self.__register_tuple(value=None, num_bytes=32),

            "al": self.__register_tuple(value=None, num_bytes=8),
            "dil": self.__register_tuple(value=None, num_bytes=8),
            "sil": self.__register_tuple(value=None, num_bytes=8),
            "dl": self.__register_tuple(value=None, num_bytes=8),
            "cl": self.__register_tuple(value=None, num_bytes=8),
            "r8b": self.__register_tuple(value=None, num_bytes=8),
            "r9b": self.__register_tuple(value=None, num_bytes=8),
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

    def __update_reg_value(self, register, value, op):
        current_value = self.__registers[register].value

        if op == "add":
            self.__registers[register] = self.__registers[register]._replace(value=current_value + value)
        elif op == "sub":
            self.__registers[register] = self.__registers[register]._replace(value=current_value - value)
        elif op == "mul":
            self.__registers[register] = self.__registers[register]._replace(value=current_value * value)
        elif op == "assign":
            self.__registers[register] = self.__registers[register]._replace(value=value)

    def __parse_value(self, value, error_msg=None, map_to_higher_reg=False):
        old_value = value

        if map_to_higher_reg:
            register_mapping = {"al": "rax"}
            value = register_mapping[value] if value in register_mapping.keys() else value
        
        if not value.startswith("_") and value not in self.__registers.keys() and "(" not in value:
            value = int(value)
        elif "(" in value:
            index, register = value.split("(")
            mem_location = int(self.__registers[register].value) + int(index)
            value = self.__read_from_memory(mem_location=mem_location)
        else:
            if value.startswith("_"):
                if(value[1:].isdigit()):
                    value = self.__read_from_memory(mem_location=value)
                else:
                    value = self.__read_from_memory(mem_location=self.__registers[value[1:]].value)
            else:
                value = self.__registers[value].value

        if value == None and error_msg != None:
            error_utils.error(msg=error_msg.replace("{}", old_value))
        elif value == None and error_msg == None:
            value = -1

        return value

    def __execute_push_to_stack(self, value):
        value = self.__parse_value(
            value=value,
            error_msg="Register '{}' has not been set, you cannot push it to stack"
        )

        self.__stack.append(value)

        self.__update_reg_value(register="rsp", value=8, op="add")

    def __execute_pop_from_stack(self, register):
        value = self.__stack.pop()
        update_value = int(value) if type(value) != int and not value.startswith("_") and not value.startswith("g_") else value
        self.__update_reg_value(register=register, value=update_value, op="assign")
        
        self.__update_reg_value(register="rsp", value=8, op="sub")

    def __compute_true_mem_loc(self, mem_location):
        if type(mem_location) == int:
            return mem_location

        mem_location = -1 * int(mem_location[1:]) + self.__registers["rbp"].value if mem_location[1:].isdigit() and mem_location[0] == "_" else mem_location
        return int(mem_location) if type(mem_location) == str and mem_location.isdigit() else mem_location

    def __store_in_memory(self, mem_location, value, bits):
        mem_location = self.__compute_true_mem_loc(mem_location)

        if type(value) == int and type(mem_location) == int and value > 0 and bits != 8:
            value = bin(value)[2:]
            value = '0' * (bits - len(value)) + value
            value = [value[i*8:(i+1)*8] for i in range(bits//8)]
            value = [int(binary, 2) for binary in value]
            value = value[::-1]
            for i in range(bits//8):
                self.__memory[mem_location+i] = value[i]
        else:
            self.__memory[mem_location] = value

    def __read_from_memory(self, mem_location):
        mem_location = self.__compute_true_mem_loc(mem_location)
        return self.__memory.get(mem_location, None)

    def __execute_move_instruction(self, value, register):
        bits = 64
        if type(value) == str and not value.isdigit() and value != "r8" and (value.endswith("8") or value == "al"):
            value = value[:-1] if value != "al" else value
            bits = 8

        map_to_higher_reg = True if "(" in register or register.startswith("_") else False
        value = self.__parse_value(
            value=value,
            map_to_higher_reg=map_to_higher_reg
        )
        
        if register.startswith("_"):
            if(register[1:].isdigit()):
                self.__store_in_memory(mem_location=register, value=value, bits=bits)
            else:
                self.__store_in_memory(mem_location=self.__registers[register[1:]].value, value=value, bits=bits)
        elif "(" in register:
            index, register = register.split("(")
            mem_location = int(self.__registers[register].value) + int(index)
            self.__store_in_memory(mem_location=mem_location, value=value, bits=bits)
        else:
            if self.__get_opcode_from_pos().op_code == "movsbq" and value > 256:
                value =  int(bin(value)[-8:], 2)
            self.__update_reg_value(register=register, value=value, op="assign")

    def __execute_return_instruction(self):
        if len(self.__call_stack) == 0:
            for value in self.__registers.values():
                if value.value != None:
                    value = value.value
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
        if self.__registers[register].value == None:
            error_utils.error(
                msg=f"Register {register} does not have any value, set a value to perform arithmetic operation"
            )

        value = self.__parse_value(
            value=value,
            error_msg="Register {} has not been set, you cannot perform " + operator + " operation"
        )

        new_value = 0
        existing_reg_value = self.__registers[register].value

        if type(existing_reg_value) == str and existing_reg_value.startswith("g_") and not existing_reg_value.startswith("g__"):
            existing_reg_value = self.__read_from_memory(mem_location=existing_reg_value)

        if type(value) == str and value.startswith("_"):
            value = -1 * int(value[1:])

        is_global_str_literal = True if type(existing_reg_value) == str and existing_reg_value.startswith("g__") else False
        if is_global_str_literal:
            value = str(value)

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

        new_value = new_value if not register_is_mem_loc else "_" + str(-1 * new_value)
        self.__update_reg_value(register=register, value=new_value, op="assign")

    def __execute_unary_operation(self, register):
        if self.__registers[register].value == None:
            error_utils.error(msg=f"Register '{register}' has not been set, cannot negate empty value")

        self.__update_reg_value(register=register, value=-1, op="mul")

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

        register = register[:-1] if type(register) == str and register.endswith("8") else register

        if operator == "sete":
            if zero_flag_val == 1:
                self.__update_reg_value(register=register, value=1, op="assign")
            elif zero_flag_val == 0:
                self.__update_reg_value(register=register, value=0, op="assign")
        elif operator == "setne":
            if zero_flag_val == 1:
                self.__update_reg_value(register=register, value=0, op="assign")
            elif zero_flag_val == 0:
                self.__update_reg_value(register=register, value=1, op="assign")
        elif operator == "setl":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__update_reg_value(register=register, value=1, op="assign")
            else:
                self.__update_reg_value(register=register, value=0, op="assign")
        elif operator == "setle":
            if negative_flag_val == 1 and positive_flag_val == 0:
                self.__update_reg_value(register=register, value=1, op="assign")
            elif zero_flag_val == 1:
                self.__update_reg_value(register=register, value=1, op="assign")
            else:
                self.__update_reg_value(register=register, value=0, op="assign")

        self.__clear_flags()

    def __execute_lea(self, address, register):
        self.__update_reg_value(register=register, value=self.__compute_true_mem_loc(address), op="assign")

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
        self.__store_in_memory(mem_location=global_var_name, value=0, bits=64)

    def execute(self, yield_execution=False, show_exec_opcodes=False):
        current_global_var = None
        current_global_val_idx = 0
        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if show_exec_opcodes:
                print(op_code)

            if op_code.op_code == "global":
                global_var_name = op_code.op_value
                current_global_var = global_var_name
                current_global_val_idx = 0
                self.__execute_global_var(global_var_name=global_var_name)
                self.__increment_opcode_ptr()
            elif op_code.op_code == "byte":
                value = int(op_code.op_value)
                value = 256 - abs(value) if value < 0 else value
                self.__store_in_memory(mem_location=current_global_var + str(current_global_val_idx), value=value, bits=8)
                current_global_val_idx += 1
                self.__increment_opcode_ptr()
            else:
                break

        main_opcode = opcode.OpCode(op_code="label", op_value="main", line_num=1)
        main_opcode_idx = self.__find_opcode_idx(op=main_opcode)

        if main_opcode_idx != None:
            self.__current_opcode_ptr = main_opcode_idx

        while not self.__is_opcode_list_end():
            op_code = self.__get_opcode_from_pos()

            if show_exec_opcodes:
                print(op_code)

            if op_code.op_code in ["mov", "movzb", "movsbq"]:
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
                    "registers": {register: self.__registers[register].value for register in self.__registers.keys()},
                    "memory": self.__memory,
                    "stack": self.__stack,
                }

        if yield_execution:
            yield self.__registers["rax"].value
        else:
            return self.__registers["rax"].value