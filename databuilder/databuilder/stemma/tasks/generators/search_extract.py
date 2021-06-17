import logging
import os
import uuid
from typing import Any, Dict

from elasticsearch import Elasticsearch
from pyhocon import ConfigFactory

from databuilder.extractor.neo4j_search_data_extractor import Neo4jSearchDataExtractor
from databuilder.job.job import DefaultJob
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.publisher.elasticsearch_constants import (
    DASHBOARD_ELASTICSEARCH_INDEX_MAPPING, USER_ELASTICSEARCH_INDEX_MAPPING,
)
from databuilder.publisher.elasticsearch_publisher import ElasticsearchPublisher
from databuilder.stemma.tasks.generators.base_task_generator import TaskGenerator
from databuilder.task.task import DefaultTask
from databuilder.transformer.base_transformer import NoopTransformer

LOGGER = logging.getLogger(__name__)

ENTITY_TYPE_MAPPINGS = {
    'table': {
        'model_name': 'databuilder.models.table_elasticsearch_document.TableESDocument',
        'mapping': None
    },
    'user': {
        'model_name': 'databuilder.models.user_elasticsearch_document.UserESDocument',
        'mapping': USER_ELASTICSEARCH_INDEX_MAPPING
    },
    'dashboard': {
        'model_name': 'databuilder.models.dashboard_elasticsearch_document.DashboardESDocument',
        'mapping': DASHBOARD_ELASTICSEARCH_INDEX_MAPPING
    }
}


class SearchIndexTaskGenerator(TaskGenerator):
    """
    A base generator that can extract any type of object to an ElasticSearch
    index. For example, tables, users, dashboards.
    """
    EXTRACTOR_CLASS = Neo4jSearchDataExtractor  # type: ignore
    EXTRACT_SEARCH_DATA_PATH = '/var/tmp/amundsen/search_data.json'

    def __init__(self) -> None:
        es_host = os.getenv("ES_HOST", "host.docker.internal")
        es_port = os.getenv("ES_PORT", 9200)
        self.es_client = Elasticsearch([
            {'host': es_host, 'port': es_port},
        ])
        super().__init__()

    def try_load_conn_secrets(self) -> None:
        """
        This should be the only class that does not require separate connection secrets
        since Neo4j and Elasticsearch are the only two connections. The login credentials
        for these connections should be top-level objects.
        """
        pass

    def _generate_base_confs(self) -> None:
        job_config_dict = {
            'extractor.search_data.extractor.neo4j.graph_url': self.NEO4J_ENDPOINT,
            'extractor.search_data.extractor.neo4j.neo4j_auth_user': self.neo4j_user,
            'extractor.search_data.extractor.neo4j.neo4j_auth_pw': self.neo4j_password,
            'extractor.search_data.extractor.neo4j.neo4j_encrypted': False,
            'loader.filesystem.elasticsearch.file_path': self.EXTRACT_SEARCH_DATA_PATH,
            'loader.filesystem.elasticsearch.mode': 'w',
            'publisher.elasticsearch.file_path': self.EXTRACT_SEARCH_DATA_PATH,
            'publisher.elasticsearch.mode': 'r',
            'publisher.elasticsearch.client': self.es_client
        }
        self.conf_dict = job_config_dict.copy()

    def _update_base_confs(self, entity_type: str) -> Dict[str, Any]:
        model_name = ENTITY_TYPE_MAPPINGS[entity_type]['model_name']  # type: ignore
        index_alias = f'{entity_type}_search_index'
        new_index_key = f'{entity_type}_{uuid.uuid4()}'

        updated_confs = self.conf_dict.copy()
        updated_confs.update({
            'publisher.elasticsearch.doc_type': entity_type,
            'extractor.search_data.entity_type': entity_type,
            'extractor.search_data.extractor.neo4j.model_class': model_name,
            'publisher.elasticsearch.new_index': new_index_key,
            'publisher.elasticsearch.alias': index_alias
        })
        return updated_confs

    def launch_job(self) -> None:
        for task in ENTITY_TYPE_MAPPINGS:
            LOGGER.info('Starting search index extract for task: %s' % task)
            task_conf = self._update_base_confs(task)
            run_task = DefaultTask(loader=FSElasticsearchJSONLoader(),
                                   extractor=self.extractor_instance,
                                   transformer=NoopTransformer())
            job = DefaultJob(conf=ConfigFactory.from_dict(task_conf),
                             task=run_task,
                             publisher=ElasticsearchPublisher())
            job.launch()
