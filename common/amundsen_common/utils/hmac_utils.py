import hashlib
import hmac
import json
from typing import Dict, Any

ENCODING = 'latin-1'


def generate_token(secret: str, data: Dict[Any, Any]) -> str:
    """
    Takes data dictionary and secret, and generate a new hmac token
    """
    payload = json.dumps(data)
    return hmac.new(bytes(secret, ENCODING),
                    msg=bytes(payload, ENCODING),
                    digestmod=hashlib.sha256).hexdigest().upper()


def verify_token(request_token: str, secret: str, data: bytes) -> bool:
    """
    Compare tokens
    """
    token = hmac.new(bytes(secret, ENCODING), msg=data,
                     digestmod=hashlib.sha256).hexdigest().upper()

    return hmac.compare_digest(token, request_token)
