from config_builder.app.frontend.auth import AuthConf
from config_builder.app.frontend.mode import ModeConf
from config_builder.generator.stemma_conf import StemmaConfGenerator


class FrontendAppConf(StemmaConfGenerator):
    """
    All configuration options supported by the Stemma Frontend APP
    """
    auth: AuthConf = AuthConf()
    mode: ModeConf = ModeConf()
