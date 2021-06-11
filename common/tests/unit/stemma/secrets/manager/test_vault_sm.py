import json
import unittest
import responses  # type: ignore
from test.support import EnvironmentVarGuard  # type: ignore
from unittest.mock import patch, mock_open
from amundsen_common.stemma.secrets.manager.base import SecretManagerException
from amundsen_common.stemma.secrets.manager.vault import VaultSecretManager


class TestVaultSecretManager(unittest.TestCase):
    def setUp(self) -> None:
        self.env = EnvironmentVarGuard()
        self.env.set('JWT_PATH', '/token.json')

    @responses.activate
    def test_vault_sm_defaults(self) -> None:
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
                default_vm = VaultSecretManager(
                    'secret',
                    {
                        'role': VaultSecretManager.DEFAULT_ACCESS_ROLE,
                    },
                )

                self.assertEqual(
                    responses.calls[0].request.body.decode('utf-8'),
                    json.dumps(
                        {'role': VaultSecretManager.DEFAULT_ACCESS_ROLE, 'jwt': 'thisisthetoken'},
                    ),
                )
                self.assertEqual(default_vm.secrets['secret'], 'one')

    @responses.activate
    def test_vault_auth_fail(self) -> None:
        responses.add(
            responses.PUT,
            f'{VaultSecretManager.DEFAULT_HOST_PORT}/v1/{VaultSecretManager.DEFAULT_AUTH_PATH}',
            json={'notauth': {'client_token': 'auth_token_issued'}},
            status=200,
        )

        with self.env:
            with patch('builtins.open', mock_open(read_data='thisisthetoken')):
                with self.assertRaisesRegex(SecretManagerException, 'authenticating'):
                    VaultSecretManager(
                        'secret',
                        {
                            'role': VaultSecretManager.DEFAULT_ACCESS_ROLE,
                        },
                    )

    @responses.activate
    def test_vault_secret_load_fail(self) -> None:
        responses.add(
            responses.PUT,
            f'{VaultSecretManager.DEFAULT_HOST_PORT}/v1/{VaultSecretManager.DEFAULT_AUTH_PATH}',
            json={'auth': {'client_token': 'auth_token_issued'}},
            status=200,
        )
        responses.add(
            responses.GET,
            f'{VaultSecretManager.DEFAULT_HOST_PORT}/v1/secret',
            json={'nodata': {}},
            status=200,
        )

        with self.env:
            with patch('builtins.open', mock_open(read_data='thisisthetoken')):
                with self.assertRaisesRegex(SecretManagerException, 'retrieving'):
                    VaultSecretManager(
                        'secret',
                        {
                            'role': VaultSecretManager.DEFAULT_ACCESS_ROLE,
                        },
                    )
                with self.assertRaisesRegex(SecretManagerException, 'VAULT_SECRET_PATH'):
                    VaultSecretManager(
                        None,
                        {
                            'role': VaultSecretManager.DEFAULT_ACCESS_ROLE,
                        },
                    )
