import base64


def to_hash(num: int) -> str:
    "hash a integer to a url safe base64 enconding, assures the output is 8 characters long"
    return base64.urlsafe_b64encode(num.to_bytes(length=6)).decode()


def from_hash(hash: str) -> int:
    "decode a 8 charater hash to a integer"
    return int.from_bytes(base64.urlsafe_b64decode(hash))
