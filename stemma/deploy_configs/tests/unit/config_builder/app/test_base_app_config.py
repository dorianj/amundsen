import unittest

from config_builder.app.base import BaseAppConf
from config_builder.app.frontend.base import FrontendAppConf


class TestBaseAppConf(unittest.TestCase):

    def setUp(self) -> None:
        self.defaultBase = BaseAppConf(frontend=FrontendAppConf())

    def test_base_defaults(self) -> None:
        defaultEnv = self.defaultBase.build_env()
        self.assertIn({'key': 'FRONTEND_IMAGE_TAG', 'value': 'latest'}, defaultEnv)
        self.assertIn({'key': 'FRONTEND_APP_CLASS', 'value': 'FlaskOIDC'}, defaultEnv)
