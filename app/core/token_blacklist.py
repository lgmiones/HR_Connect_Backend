# Simple in-memory token blacklist
revoked_tokens = set()

def add_to_blacklist(token: str):
    revoked_tokens.add(token)

def is_token_revoked(token: str) -> bool:
    return token in revoked_tokens
