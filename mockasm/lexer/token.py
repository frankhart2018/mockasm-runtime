class Token:
    def __init__(self, lexeme, token_type, line_num):
        self.lexeme = lexeme
        self.token_type = token_type
        self.line_num = line_num

    def __str__(self):
        return f"Token(lexeme={self.lexeme}, token_type={self.token_type}, line_num={self.line_num})"

    def __eq__(self, other):
        return self.lexeme == other.lexeme and self.token_type == other.token_type and self.line_num == other.line_num