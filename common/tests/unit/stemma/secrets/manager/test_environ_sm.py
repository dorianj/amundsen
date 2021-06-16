import json
import unittest
from test.support import EnvironmentVarGuard  # type: ignore
from amundsen_common.stemma.secrets.manager.base import SecretManagerException
from amundsen_common.stemma.secrets.manager.environ import EnvironSecretManager


class TestEnvironSecretManager(unittest.TestCase):

    def setUp(self) -> None:
        self.env = EnvironmentVarGuard()
        self.env.set(EnvironSecretManager.DEFAULT_ENVIRON_KEY, json.dumps({'secret': 'one'}))
        self.env.set('another_env_key', json.dumps({'secret': 'two'}))
        self.env.set('empty_env_key', json.dumps(''))
        self.env.set('invalid_env_key', '{"secert":5+3}')

    def test_environ_happy(self) -> None:
        with self.env:
            default_sm = EnvironSecretManager()
            self.assertEqual(default_sm.secrets['secret'], 'one')

            custom_sm = EnvironSecretManager('another_env_key')
            self.assertEqual(custom_sm.secrets['secret'], 'two')

            override_sm = EnvironSecretManager(None, {'secrets': {'secret': True}})
            self.assertTrue(override_sm.secrets['secret'])

    def test_environ_errors(self) -> None:
        with self.env:
            with self.assertRaisesRegex(SecretManagerException, 'requires an encoded'):
                EnvironSecretManager('empty_env_key')
