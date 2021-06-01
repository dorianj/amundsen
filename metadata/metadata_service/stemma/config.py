from metadata_service.config import LocalConfig
from metadata_service.stemma import init_custom_apps_and_routes


class StemmaConfig(LocalConfig):
    PROXY_CLIENT = 'metadata_service.stemma.stemma_proxy.StemmaProxy'

    INIT_CUSTOM_EXT_AND_ROUTES = init_custom_apps_and_routes
