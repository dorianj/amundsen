
from config_builder.app.base import BaseAppConf

iRobot = BaseAppConf(
    METADATA_PROXY_HOST='localhost',
    METADATA_PROXY_USER='neo4j',
    METADATA_IMAGE_TAG='latest'
)
