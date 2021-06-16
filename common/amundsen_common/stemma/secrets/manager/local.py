import logging
import os
from typing import Any, Dict, Optional

from amundsen_common.stemma.secrets.manager.base import BaseSecretManager

LOGGER = logging.getLogger(__name__)


class LocalSecretManager(BaseSecretManager):
    """
    Secret manager that uses environment variables. Should be used localnly.
    """
    DEFAULT_CONN: Dict[str, str] = {
        'USERNAME': 'username',
        'PASSWORD': 'password',
        'ACCOUNT': 'account',
        'WAREHOUSE': 'warehouse'
    }

    SNOWFLAKE_LOCAL: Dict[str, Any] = {
        'TYPE': 'snowflake',
        # Make sure you have the connection details in your environment variables
        'DATABASES': [
            {
                "METADATA": True,
                "NAME": "\"ca_covid\"",
                "STATS": True
            },
            {
                "METADATA": True,
                "NAME": "SNOWFLAKE_SAMPLE_DATA",
                "STATS": True
            }
        ]
    }

    def _load_secrets(self, key: Optional[str] = None, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Loads secrets from a json serialized in an environment variable.
        Options are not applicable for environment loading.
        """
        conn = {}
        for key in self.DEFAULT_CONN.keys():
            conn[key] = os.environ.get(key, self.DEFAULT_CONN[key])

        return {**self.SNOWFLAKE_LOCAL, 'CONN': conn}
