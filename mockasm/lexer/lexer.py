from . import token
from ..utils import error_utils
from mockasm import lexer


class Lexer:
    def __init__(self, source_code):
        self.__source_code = source_code
        self.__line_num = 1
        self.__current_source_ptr = 0
        self.__tokens = []

        self.__opcodes = [
            "mov",
            "movzb",
            "ret",
            "add",
            "sub",
            "imul",
            "idiv",
            "cqo",
            "neg",
            "push",
            "pop",
            "cmp",
            "sete",
            "setne",
            "setl",
            "setle",
            "lea",
            "jmp",
            "je",
            "call",
        ]

        self.__registers = [
            "rax",
            "rdi",
            "al",
        ]

    def __get_char_from_pos(self, pos=None):
        return (
            self.__source_code[self.__current_source_ptr]
            if pos == None
            else self.__source_code[pos]
        )

    def __increment_source_ptr(self, by=None):
        self.__current_source_ptr += 1 if by == None else by

    def __increment_line_num(self):
        self.__line_num += 1

    def __is_source_end(self):
        return self.__current_source_ptr >= len(self.__source_code)

    def __append_token(self, token):
        self.__tokens.append(token)

    def __is_keyword(self, lexeme):
        return lexeme in self.__opcodes

    def __is_register(self, lexeme):
        return lexeme in self.__registers

    def __identify_keyword(self):
        lexeme = ""
        while not self.__is_source_end():
            char = self.__get_char_from_pos()
            if not char.isalpha():
                break

            lexeme += char
            self.__increment_source_ptr()

        if self.__is_keyword(lexeme=lexeme):
            return token.Token(
                lexeme=lexeme, token_type=lexeme, line_num=self.__line_num
            )
        elif self.__is_register(lexeme=lexeme):
            return token.Token(
                lexeme=lexeme, token_type="register", line_num=self.__line_num
            )

        error_utils.error(msg=f"{lexeme} is not a keyword or a register")

    def __identify_number(self):
        lexeme = ""
        while not self.__is_source_end():
            char = self.__get_char_from_pos()
            if not char.isdigit():
                break

            lexeme += char
            self.__increment_source_ptr()

        return token.Token(lexeme=lexeme, token_type="number", line_num=self.__line_num)

    def __identify_location_at(self):
        self.__increment_source_ptr()

        temp_token = self.__identify_keyword()
        
        current_char = self.__get_char_from_pos()
        if current_char == ")":
            return token.Token(
                lexeme=f"{temp_token.lexeme}", token_type="location_at", line_num=temp_token.line_num
            )
        
        error_utils.error(msg="Missing closing parantheses in location_at register")

    def __identify_label(self):
        self.__increment_source_ptr()
        self.__increment_source_ptr()

        lexeme = ""

        while not self.__is_source_end():
            char = self.__get_char_from_pos()
            if not char.isalpha() and char != '_' and not char.isdigit():
                break

            lexeme += char
            self.__increment_source_ptr()

        return token.Token(
            lexeme=lexeme, token_type="label", line_num=self.__line_num
        )

    def __skip_comments(self):
        while not self.__is_source_end():
            char = self.__get_char_from_pos()
            if char == '\n':
                break

            self.__increment_source_ptr()

    def lexical_analyze(self):
        while not self.__is_source_end():
            char = self.__get_char_from_pos()

            if char.isalpha():
                current_token = self.__identify_keyword()
                self.__append_token(token=current_token)
            elif char == "$":
                self.__increment_source_ptr()
                
                is_address = False
                current_char = self.__get_char_from_pos()
                if current_char == '_':
                    is_address = True
                    self.__increment_source_ptr()

                current_token = self.__identify_number()

                if is_address:
                    current_token = token.Token(
                        lexeme=current_token.lexeme,
                        token_type="address",
                        line_num=current_token.line_num
                    )

                self.__append_token(token=current_token)
            elif char == "\n":
                self.__increment_line_num()
                self.__increment_source_ptr()
            elif char == ",":
                current_token = token.Token(
                    lexeme=",", token_type="comma", line_num=self.__line_num
                )
                self.__append_token(token=current_token)
                self.__increment_source_ptr()
            elif char == "(":
                current_token = self.__identify_location_at()
                self.__append_token(token=current_token)
            elif char == ".":
                self.__increment_source_ptr()
                current_char = self.__get_char_from_pos()
                if current_char == "L":
                    current_token = self.__identify_label()
                    self.__append_token(token=current_token)
                else:
                    self.__increment_source_ptr()
            elif char == ':':
                self.__append_token(token.Token(
                    lexeme=':', token_type='colon', line_num=self.__line_num
                ))
                self.__increment_source_ptr()
            elif char == '#':
                self.__skip_comments()
            else:
                self.__increment_source_ptr()

        return self.__tokens
