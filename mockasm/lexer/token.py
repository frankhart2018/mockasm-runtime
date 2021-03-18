class Token:
    def __init__(self, lexeme, token_type, line_num):
        self.lexeme = lexeme
        self.token_type = token_type
        self.line_num = line_num

    def __str__(self):
        return f"Token(lexeme=\033[91m{self.lexeme}\033[m, token_type=\033[91m{self.token_type}\033[m, line_num=\033[91m{self.line_num}\033[m)"

    def __eq__(self, other):
        return self.lexeme == other.lexeme and self.token_type == other.token_type and self.line_num == other.line_num