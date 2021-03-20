from . import error_utils


def match_tokens(current_token_type, expected_token_types, error_msg):
    if current_token_type in expected_token_types:
        return True

    error_utils.error(msg=error_msg)
