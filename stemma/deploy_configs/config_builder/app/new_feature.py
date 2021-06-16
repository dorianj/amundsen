
from .base import BaseAppConf


class NewFeatureConf(BaseAppConf):
    """
    Example of a config enabling a feature flag
    """
    NEWEST_FEATURE = True
    METADATA_IMAGE_TAG = 'Even newer metadata tag'
