"""
Most generic application specific configuraiton.
This SHOULD be a flat set of attributes, ideally there should not be objects assigned as values.

The BaseAppConf should reference every potential configuration that exists
for Stemma. Other configurations may inherit and override where needed.
Each client configuration would build their configs from a given
conf class. For example:

client_conf = BaseAppConf(
    FRONTEND_IMAGE_TAG='second_newest'
)

In this example the `client_conf` object would have all of the defaults
except for the FRONTEND_IMAGE_TAG.
"""

from config_builder.app.frontend.base import FrontendAppConf
from config_builder.generator.stemma_conf import StemmaConfGenerator


class BaseAppConf(StemmaConfGenerator):
    frontend: FrontendAppConf = FrontendAppConf()
    FRONTEND_IMAGE_TAG = 'latest'
    METADATA_PROXY_HOST = 'localhost'
    METADATA_PROXY_USER = 'neo4j'
    METADATA_IMAGE_TAG = 'latest'
