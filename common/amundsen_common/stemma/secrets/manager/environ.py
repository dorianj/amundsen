import json
import logging
import os
from typing import Any, Dict, Optional

from amundsen_common.stemma.secrets.manager.base import BaseSecretManager, SecretManagerException


LOGGER = logging.getLogger(__name__)


class EnvironSecretManager(BaseSecretManager):
    """
    Secret manager that uses environment variables. Should be used localnly.
    """

    DEFAULT_ENVIRON_KEY = 'ENV_SECRET_MANAGER'

    def _load_secrets(self, key: Optional[str] = None, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Loads secrets from a json serialized in an environment variable.
        Options are not applicable for environment loading.
        """

        # Short circuit if overriding secrets dictionary
        if 'secrets' in options:
            return options['secrets']

        serialized_secrets = os.environ.get(key if key is not None else self.DEFAULT_ENVIRON_KEY, '')

        try:
            loaded_secrets = json.loads(serialized_secrets)
        except Exception as e:
            LOGGER.error(f'Exception on json parsing {e}')
            raise SecretManagerException(f'Environ json serialization failed for key: {key}')

        if type(loaded_secrets) != dict:
            LOGGER.error(f'Unexpected value type in secrets {type(loaded_secrets)}')
            raise SecretManagerException(f'Environ secret manager requires an encoded json object in the key : {key}')

        return loaded_secrets
