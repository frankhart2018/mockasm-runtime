class Token:
    def __init__(self, lexeme, token_type, line_num):
        self.__lexeme = lexeme
        self.__token_type = token_type
        self.__line_num = line_num

    @property
    def lexeme(self):
        return self.__lexeme

    @property
    def token_type(self):
        return self.__token_type

    @property
    def line_num(self):
        return self.__line_num

    def __str__(self):
        return f"Token(lexeme=\033[91m{self.lexeme}\033[m, token_type=\033[91m{self.token_type}\033[m, line_num=\033[91m{self.line_num}\033[m)"

    def __eq__(self, other):
        return self.lexeme == other.lexeme and self.token_type == other.token_type and self.line_num == other.line_num