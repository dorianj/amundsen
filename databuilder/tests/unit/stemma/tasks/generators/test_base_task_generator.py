import unittest

import pytest

from databuilder.stemma.tasks.generators.base_task_generator import InvalidSecretsException, TaskGenerator


class TestBaseTaskGenerators(unittest.TestCase):

    def setUp(self) -> None:
        self.generator = TaskGenerator()
        self.maxDiff = None

    def test_get_task_generator(self) -> None:
        expected = {
            'loader.filesystem_csv_neo4j.delete_created_directories': True,
            'loader.filesystem_csv_neo4j.force_create_directory': True,
            'loader.filesystem_csv_neo4j.node_dir_path': '/var/tmp/amundsen/tables/nodes',
            'loader.filesystem_csv_neo4j.relationship_dir_path': '/var/tmp/amundsen/tables/relationships',
            'publisher.neo4j.neo4j_endpoint': 'bolt://host.docker.internal:7687',
            'publisher.neo4j.neo4j_password': 'test',
            'publisher.neo4j.neo4j_user': 'neo4j',
            'publisher.neo4j.node_files_directory': '/var/tmp/amundsen/tables/nodes',
            'publisher.neo4j.relation_files_directory': '/var/tmp/amundsen/tables/relationships'
        }
        self.generator.conf_dict.pop('publisher.neo4j.job_publish_tag')  # uses UUID
        self.assertEqual(self.generator.conf_dict, expected)

    def test_required_secrets(self) -> None:
        self.generator.REQUIRED_SECRETS = ['SECRET_VAL']

        with pytest.raises(InvalidSecretsException):
            self.generator.validate_secrets()

        self.generator.conn_secrets['SECRET_VAL'] = 'anything'
        self.generator.validate_secrets()
        self.generator.conn_secrets.pop('SECRET_VAL')
        self.generator.REQUIRED_SECRETS = []
        self.assertTrue(True)
