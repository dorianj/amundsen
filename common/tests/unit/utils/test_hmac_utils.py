import json
import unittest

from amundsen_common.utils.hmac_utils import generate_token, verify_token, ENCODING


class TestHmacUtils(unittest.TestCase):
    SECRET = "!secret"
    payload = {"alpha": "beta"}

    def test_generates_token(self) -> None:
        token = generate_token(self.SECRET, self.payload)
        self.assertIsNotNone(token)

    def test_verifies_token(self) -> None:
        token = generate_token(self.SECRET, self.payload)
        is_verified = verify_token(token, self.SECRET,
                                   bytes(json.dumps(self.payload), ENCODING))
        self.assertTrue(is_verified)
