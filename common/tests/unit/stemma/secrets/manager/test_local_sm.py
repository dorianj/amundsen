import unittest
from test.support import EnvironmentVarGuard  # type: ignore
from amundsen_common.stemma.secrets.manager.local import LocalSecretManager


class TestLocalSecretManager(unittest.TestCase):
    def setUp(self) -> None:
        self.env = EnvironmentVarGuard()
        self.env.set('PASSWORD', 'apass')

    def test_local_secret_merge(self) -> None:
        sm = LocalSecretManager()
        self.assertEqual('account', sm.secrets['CONN']['ACCOUNT'])
        self.assertEqual('apass', sm.secrets['CONN']['PASSWORD'])
