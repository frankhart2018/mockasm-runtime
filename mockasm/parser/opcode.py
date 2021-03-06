class OpCode:
    def __init__(self, op_code, op_value, line_num):
        self.__op_code = op_code
        self.__op_value = op_value
        self.__line_num = line_num

    @property
    def op_code(self):
        return self.__op_code

    @property
    def op_value(self):
        return self.__op_value

    @property
    def line_num(self):
        return self.__line_num

    @op_value.setter
    def op_value(self, op_value):
        self.__op_value = op_value

    def __str__(self):
        return f"OpCode(op_code=\033[91m{self.op_code}\033[m, op_value=\033[91m{self.op_value}\033[m, line_num=\033[91m{self.line_num}\033[m)"

    def __eq__(self, other):
        return self.op_code == other.op_code and self.op_value == other.op_value
