class OpCode:
    def __init__(self, op_code, op_value):
        self.__op_code = op_code
        self.__op_value = op_value

    @property
    def op_code(self):
        return self.__op_code

    @property
    def op_value(self):
        return self.__op_value

    def __str__(self):
        return f"OpCode(op_code=\033[91m{self.op_code}\033[m, op_value=\033[91m{self.op_value}\033[m)"

    def __eq__(self, other):
        return self.op_code == other.op_code and self.op_value == other.op_value