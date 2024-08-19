import base64

from sqlalchemy import Column

# TODO: add cipher to hash function


def to_hash(num: int | Column[int]) -> str:
    "hash a integer to a URL safe base64 encoding, assures the output is 8 characters long"
    return base64.urlsafe_b64encode(num.to_bytes(length=6)).decode()


def from_hash(hash: str | Column[str]) -> int:
    "decode a 8 charter hash to a integer"
    return int.from_bytes(base64.urlsafe_b64decode(hash))


def valid_hash(hash: str) -> bool:
    "check if hash is valid base64 format with 8 characters"

    if not isinstance(hash, str):
        return False
    if len(hash) != 8:
        return False

    try:  # test if bijection holds
        num = from_hash(hash)
        return hash == to_hash(num)
    except Exception as exp:
        return False
