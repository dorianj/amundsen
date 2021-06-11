import json
import unittest
import responses  # type: ignore
from test.support import EnvironmentVarGuard  # type: ignore
from unittest.mock import patch, mock_open
from amundsen_common.stemma.secrets import get_secrets_manager
from amundsen_common.stemma.secrets.manager.environ import EnvironSecretManager
from amundsen_common.stemma.secrets.manager.vault import VaultSecretManager


class TestGetSecretsManager(unittest.TestCase):

    def setUp(self) -> None:
        self.env = EnvironmentVarGuard()
        self.env.set(EnvironSecretManager.DEFAULT_ENVIRON_KEY, json.dumps({'secret': 'one'}))
        self.env.set('JWT_PATH', '/token.json')

    def test_default_is_environ(self) -> None:
        sm = get_secrets_manager()
        self.assertIsInstance(sm, EnvironSecretManager)

    @responses.activate
    def test_vault_from_env(self) -> None:
        self.env.set('SECRET_MANAGER_CLASS', 'amundsen_common.stemma.secrets.manager.vault.VaultSecretManager')

        responses.add(
            responses.PUT,
            f'{VaultSecretManager.DEFAULT_HOST_PORT}/v1/{VaultSecretManager.DEFAULT_AUTH_PATH}',
            json={'auth': {'client_token': 'auth_token_issued'}},
            status=200,
        )
        responses.add(
            responses.GET,
            f'{VaultSecretManager.DEFAULT_HOST_PORT}/v1/secret',
            json={'data': {'data': {'secret': 'one'}}},
            status=200,
        )

        with self.env:
            with patch('builtins.open', mock_open(read_data='thisisthetoken')):
                sm = get_secrets_manager('secret')
                self.assertIsInstance(sm, VaultSecretManager)
