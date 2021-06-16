import logging
import os
import uuid
from typing import (
    Any, Dict, List, Optional,
)

from amundsen_common.stemma.secrets import get_secrets_manager
from pyhocon import ConfigFactory

from databuilder.extractor.base_extractor import Extractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_neo4j_csv_loader import FsNeo4jCSVLoader
from databuilder.publisher import neo4j_csv_publisher
from databuilder.publisher.neo4j_csv_publisher import Neo4jCsvPublisher
from databuilder.task.task import DefaultTask

LOGGER = logging.getLogger(__name__)

STEMMA_ENV_PREFIX = 'STEMMA_'
DEFAULT_STEMMA_NEO4J_SECRET_LOC = 'secret/stemma/neo4j'
STEMMA_NEO4J_SECRET_LOC = os.environ.get('STEMMA_NEO4J_SECRET_LOC', DEFAULT_STEMMA_NEO4J_SECRET_LOC)


class InvalidSecretsException(Exception):
    pass


class TaskGenerator(object):

    EXTRACTOR_CLASS: Optional[Extractor] = None
    REQUIRED_SECRETS: List[str] = []

    TMP_FOLDER = '/var/tmp/amundsen/tables'
    NODE_FILES_FOLDER = f'{TMP_FOLDER}/nodes'
    RELATIONSHIP_FILES_FOLDER = f'{TMP_FOLDER}/relationships'

    NEO4J_ENDPOINT = f'bolt://{os.getenv("NEO4J_HOST", "host.docker.internal")}:7687'

    def __init__(self) -> None:
        super().__init__()
        config_inputs = {}
        for envvar, envval in os.environ.items():
            if envvar.lower().startswith(STEMMA_ENV_PREFIX.lower()):
                config_inputs[envvar.replace(STEMMA_ENV_PREFIX, '')] = envval

        self.config_inputs = config_inputs

        # Data source connection secrets
        self.secrets_manager = get_secrets_manager()
        self.conn_secrets = self.secrets_manager.secrets['CONNECTION']

        # Neo4j Secrets
        self.neo4j_secret_manager = get_secrets_manager(STEMMA_NEO4J_SECRET_LOC)
        self.neo4j_user = self.neo4j_secret_manager.secrets['NEO4J_USERNAME']
        self.neo4j_password = self.neo4j_secret_manager.secrets['NEO4J_PASSWORD']

        # Create extractor object
        self.extractor_class = self.EXTRACTOR_CLASS
        self.extractor_instance = self.extractor_class() if self.extractor_class else None  # type: ignore

        # Validate secrets
        self.validate_secrets()

        # Create configs
        self.conf_dict: Dict[str, Any] = {}
        self._generate_base_confs()
        self.add_instance_confs()

    def _generate_base_confs(self) -> None:
        job_config_dict = {
            f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.NODE_DIR_PATH}': self.NODE_FILES_FOLDER,
            f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.RELATION_DIR_PATH}': self.RELATIONSHIP_FILES_FOLDER,
            f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.SHOULD_DELETE_CREATED_DIR}': True,
            f'loader.filesystem_csv_neo4j.{FsNeo4jCSVLoader.FORCE_CREATE_DIR}': True,
            f'publisher.neo4j.{neo4j_csv_publisher.NODE_FILES_DIR}': self.NODE_FILES_FOLDER,
            f'publisher.neo4j.{neo4j_csv_publisher.RELATION_FILES_DIR}': self.RELATIONSHIP_FILES_FOLDER,
            f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_END_POINT_KEY}': self.NEO4J_ENDPOINT,
            f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_USER}': self.neo4j_user,
            f'publisher.neo4j.{neo4j_csv_publisher.NEO4J_PASSWORD}': self.neo4j_password,
            f'publisher.neo4j.{neo4j_csv_publisher.JOB_PUBLISH_TAG}': f'process-{str(uuid.uuid4())}'
        }
        full_potential_confs = self.config_inputs.copy()
        # Some configs may be stored in the secrets, if the secret is also a part
        # of the pre-defined extractor config, add it to the config factory.
        full_potential_confs.update(self.conn_secrets.copy())
        for conf, conf_val in full_potential_confs.items():
            if hasattr(self.extractor_class, conf.upper()):
                _scope = self.extractor_instance.get_scope()
                _conf_item = getattr(self.extractor_class, conf.upper())
                extractor_conf_key = f'{_scope}.{_conf_item}'
                job_config_dict[extractor_conf_key] = conf_val

        self.conf_dict = job_config_dict

    def add_instance_confs(self) -> None:
        pass

    def validate_secrets(self) -> None:
        secrets_error_msg = self._validate_secrets()
        if secrets_error_msg:
            raise InvalidSecretsException(secrets_error_msg)

    def _validate_secrets(self) -> Optional[str]:
        """
        An optional hook that can be overridden and used to validate whether or not
        secrets are correct. If the secrets available do not contain the required
        values a custom error message can be returned.
        """
        missing_secrets = []
        for secret in self.REQUIRED_SECRETS:
            if secret not in self.conn_secrets:
                missing_secrets.append(secret)

        if missing_secrets:
            missing_str = ', '.join(missing_secrets)
            return f'Missing secrets for {self}, required fields: {missing_str} not provided.'
        return None

    def launch_job(self) -> None:
        csv_loader = FsNeo4jCSVLoader()
        task = DefaultTask(extractor=self.extractor_instance, loader=csv_loader)
        job = DefaultJob(conf=ConfigFactory.from_dict(self.conf_dict),
                         task=task,
                         publisher=Neo4jCsvPublisher())
        job.launch()
