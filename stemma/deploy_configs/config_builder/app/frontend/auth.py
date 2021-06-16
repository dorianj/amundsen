from config_builder.generator.stemma_conf import StemmaConfGenerator


class AuthConf(StemmaConfGenerator):
    """
    Authentication module configuration options.
    """
    FRONTEND_APP_CLASS = 'FlaskOIDC'
    FRONTEND_FLASK_APP_MODULE = 'flaskoidc'
