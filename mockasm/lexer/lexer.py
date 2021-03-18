from . import token
from ..utils import error_utils


class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.line_num = 1
        self.current_source_ptr = 0
        self.tokens = []

        self.opcodes = [
            "mov",
            "ret",
        ]

    def __get_char_from_pos(self, pos=None):
        return self.source_code[self.current_source_ptr] if pos == None else self.source_code[pos]

    def __increment_source_ptr(self, by=None):
        self.current_source_ptr += 1 if by == None else by

    def __is_source_end(self):
        return self.current_source_ptr >= len(self.source_code)

    def __append_token(self, token):
        self.tokens.append(token)

    def __is_keyword(self, lexeme):
        return lexeme in self.opcodes

    def __identify_keyword(self):
        lexeme = ""
        while not self.__is_source_end():
            char = self.__get_char_from_pos()
            if char == " " or char == "\n":
                break

            lexeme += char
            self.__increment_source_ptr()

        if not self.__is_keyword(lexeme=lexeme):
            error_utils.error(msg=f"{lexeme} is not a keyword")
            
        return token.Token(lexeme=lexeme, line_num=self.line_num)

    def lexical_analyze(self):
        while not self.__is_source_end():
            char = self.__get_char_from_pos()

            if char.isalpha():
                token = self.__identify_keyword()
                self.__append_token(token)
            elif char == " ":
                self.__increment_source_ptr()
            else:
                self.__increment_source_ptr()

        return self.tokens
