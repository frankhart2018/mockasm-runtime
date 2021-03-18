class Token:
    def __init__(self, lexeme, line_num):
        self.lexeme = lexeme
        self.line_num = line_num

    def __str__(self):
        return f"Token(lexeme={self.lexeme}, line_num={self.line_num})"

    def __eq__(self, other):
        return self.lexeme == other.lexeme and self.line_num == other.line_num