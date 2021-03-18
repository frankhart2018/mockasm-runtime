class Parser:
    def __init__(self, tokens):
        self.__tokens = tokens
        self.current_token_ptr = 0
        self.__opcodes = []

    def __is_token_list_end(self):
        return self.current_token_ptr >= len(self.__tokens)

    def parse(self):
        while not self.__is_token_list_end():
            