import os

from amundsen_application.config import LocalConfig
from amundsen_application.stemma import init_stemma_routes


class StemmaConfig(LocalConfig):
    SLACK_CONVERSATIONS_ENABLED = os.environ.get('SLACK_CONVERSATIONS_ENABLED', False)

    INIT_CUSTOM_ROUTES = init_stemma_routes
