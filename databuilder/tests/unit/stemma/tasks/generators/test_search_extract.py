import unittest

from elasticsearch import Elasticsearch

from databuilder.stemma.tasks.generators.search_extract import SearchIndexTaskGenerator


class TestSearchIndexTaskGenerator(unittest.TestCase):

    def setUp(self) -> None:
        self.generator = SearchIndexTaskGenerator()
        self.maxDiff = None

    def test_get_task_generator(self) -> None:
        expected = {
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.extractor.neo4j.neo4j_auth_pw': 'test',
            'extractor.search_data.extractor.neo4j.neo4j_auth_user': 'neo4j',
            'extractor.search_data.extractor.neo4j.neo4j_encrypted': False,
            'loader.filesystem.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'loader.filesystem.elasticsearch.mode': 'w',
            'publisher.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'publisher.elasticsearch.mode': 'r'
        }
        es_client = self.generator.conf_dict.pop('publisher.elasticsearch.client', None)
        self.assertEqual(self.generator.conf_dict, expected)
        self.assertIsInstance(es_client, Elasticsearch)

    def test_update_base_confs(self) -> None:
        tables_expected = {
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.extractor.neo4j.neo4j_auth_pw': 'test',
            'extractor.search_data.extractor.neo4j.neo4j_auth_user': 'neo4j',
            'extractor.search_data.extractor.neo4j.neo4j_encrypted': False,
            'loader.filesystem.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'loader.filesystem.elasticsearch.mode': 'w',
            'publisher.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'publisher.elasticsearch.doc_type': 'table',
            'publisher.elasticsearch.alias': 'table_search_index',
            'publisher.elasticsearch.mode': 'r',
            'extractor.search_data.extractor.neo4j.model_class': (
                'databuilder.models.table_elasticsearch_document.TableESDocument'
            ),
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.entity_type': 'table',
        }
        table_actual = self.generator._update_base_confs('table')
        _ = table_actual.pop('publisher.elasticsearch.client')
        _ = table_actual.pop('publisher.elasticsearch.new_index')
        self.assertEqual(table_actual, tables_expected)

        user_expected = {
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.extractor.neo4j.neo4j_auth_pw': 'test',
            'extractor.search_data.extractor.neo4j.neo4j_auth_user': 'neo4j',
            'extractor.search_data.extractor.neo4j.neo4j_encrypted': False,
            'loader.filesystem.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'loader.filesystem.elasticsearch.mode': 'w',
            'publisher.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'publisher.elasticsearch.doc_type': 'user',
            'publisher.elasticsearch.alias': 'user_search_index',
            'publisher.elasticsearch.mode': 'r',
            'extractor.search_data.extractor.neo4j.model_class': (
                'databuilder.models.user_elasticsearch_document.UserESDocument'
            ),
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.entity_type': 'user',
        }
        user_actual = self.generator._update_base_confs('user')
        _ = user_actual.pop('publisher.elasticsearch.client')
        _ = user_actual.pop('publisher.elasticsearch.new_index')
        self.assertEqual(user_expected, user_actual)

        dashboard_expected = {
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.extractor.neo4j.neo4j_auth_pw': 'test',
            'extractor.search_data.extractor.neo4j.neo4j_auth_user': 'neo4j',
            'extractor.search_data.extractor.neo4j.neo4j_encrypted': False,
            'loader.filesystem.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'loader.filesystem.elasticsearch.mode': 'w',
            'publisher.elasticsearch.file_path': '/var/tmp/amundsen/search_data.json',
            'publisher.elasticsearch.doc_type': 'dashboard',
            'publisher.elasticsearch.alias': 'dashboard_search_index',
            'publisher.elasticsearch.mode': 'r',
            'extractor.search_data.extractor.neo4j.model_class': (
                'databuilder.models.dashboard_elasticsearch_document.DashboardESDocument'
            ),
            'extractor.search_data.extractor.neo4j.graph_url': 'bolt://host.docker.internal:7687',
            'extractor.search_data.entity_type': 'dashboard',
        }
        dashboard_actual = self.generator._update_base_confs('dashboard')
        _ = dashboard_actual.pop('publisher.elasticsearch.client')
        _ = dashboard_actual.pop('publisher.elasticsearch.new_index')
        self.assertEqual(dashboard_expected, dashboard_actual)
