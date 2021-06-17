import logging
import os
import requests as r
from typing import Any, Dict, Optional

from http import HTTPStatus

from amundsen_common.stemma.secrets.manager.base import BaseSecretManager, SecretManagerException


LOGGER = logging.getLogger(__name__)


class VaultSecretManager(BaseSecretManager):
    """
    Secret manager to integrate with Hashicorp's Vault.
    """

    DEFAULT_ACCESS_ROLE = 'stemmaread'
    DEFAULT_AUTH_PATH = 'auth/kubernetes/login'
    DEFAULT_HOST_PORT = 'http://vault:8200'

    def _load_secrets(self, key: Optional[str] = None, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Loads a set of secrets under a path(key) from a vault instance.
        Allowed Options are:
        - role - the access role for vault.
        - jwt_path - a locally accessible path holding jwt credentials.
       """

        if 'role' not in options:
            options['role'] = os.environ.get('VAULT_ACCESS_ROLE', self.DEFAULT_ACCESS_ROLE)

        vault_path = key or os.environ.get('VAULT_SECRET_PATH')

        if not vault_path:
            raise SecretManagerException('Vault Secret Manager requires an explicit path or VAULT_SECRET_PATH set.')

        jwt_path = options['jwt_path'] if 'jwt_path' in options else os.environ['JWT_PATH']
        try:
            with open(jwt_path, 'r') as f:
                jwt = f.read()
        except Exception as e:
            LOGGER.error(f'Failed reading at path {jwt_path} with {e}')
            raise SecretManagerException(f'Vault secret manager failed reading jwt at path {jwt_path}')

        # Auth with vault to get an access token
        headers = {'Content-Type': 'application/json'}

        data = {'role': options['role'], 'jwt': jwt}

        vault_host = os.environ.get('VAULT_HOST_PORT', self.DEFAULT_HOST_PORT)
        vault_url = f'{vault_host}/v1/{self.DEFAULT_AUTH_PATH}'
        resp = r.put(vault_url, headers=headers, json=data)
        resp_json = resp.json()

        if resp.status_code != HTTPStatus.OK or 'auth' not in resp_json:
            raise SecretManagerException(f'Error authenticating with vault @ url: {vault_url}, Error: {resp_json}')
        vault_token = resp.json()["auth"]["client_token"]

        # Use the vault token to get the secrets
        headers = {'Content-Type': 'application/json', 'X-Vault-Token': vault_token}
        secret_loc_url = f'{vault_host}/v1/{vault_path}'
        secret_resp = r.get(secret_loc_url, headers=headers)

        LOGGER.info(f'Received secrets response: {secret_resp.status_code}')

        secret_resp_json = secret_resp.json()
        if 'data' not in secret_resp_json:
            raise SecretManagerException(f'Error retrieving secrets: for: {secret_loc_url}, Error: {secret_resp_json}')

        return secret_resp_json['data']['data']
