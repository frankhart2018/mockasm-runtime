from . import error_utils

def match_tokens(current_token_type, expected_token_type, error_msg):
    if current_token_type == expected_token_type:
        return True

    error_utils.error(msg=error_msg)