import pytest

from app.utils.hash import from_hash, to_hash, valid_hash


class TestHashModule:
    def test_to_hash(self):
        num = 123456789
        hash_value = to_hash(num)
        assert isinstance(hash_value, str), "The hash should be a string"
        assert len(hash_value) == 8, "The hash should be exactly 8 characters long"

    def test_from_hash(self):
        num = 123456789
        hash_value = to_hash(num)
        decoded_num = from_hash(hash_value)
        assert decoded_num == num, f"Expected {num}, got {decoded_num}"

    def test_to_hash_consistency(self):
        num = 123456789
        hash_value1 = to_hash(num)
        hash_value2 = to_hash(num)
        assert hash_value1 == hash_value2, "Hash function should be consistent"

    def test_invalid_hash_length(self):
        with pytest.raises(ValueError):
            from_hash("invalid")

    def test_valid_hash(self):
        assert valid_hash("01234567") is True
        assert valid_hash("AAAAAAAB") is True
        assert valid_hash("00000000") is True
        assert valid_hash("--------") is True

    def test_invalid_valid_hash(self):
        assert valid_hash(123) is False
        assert valid_hash(None) is False
        assert valid_hash("") is False
        assert valid_hash("0123456") is False
        assert valid_hash("012345678") is False


if __name__ == "__main__":
    pytest.main()
