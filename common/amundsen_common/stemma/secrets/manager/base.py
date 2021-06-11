from abc import abstractmethod
from typing import Any, Dict, Optional


class SecretManagerException(Exception):
    pass


class BaseSecretManager(object):
    """
    Base class for implementing secret loading and propagation to code.
    """
    def __init__(self, key: Optional[str] = None, options: Dict[str, Any] = {}) -> None:
        self.secrets: Dict[str, Any] = self._load_secrets(key, options)

    @abstractmethod
    def _load_secrets(self, key: Optional[str] = None, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Must set the internal secrets memeber with a valid Python dictionary.
        """
        pass
