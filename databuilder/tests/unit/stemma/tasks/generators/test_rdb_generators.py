import os
import unittest

from databuilder.stemma.tasks.generators.relational_db import SnowflakeTaskGenerator


class TestSnowflakeTaskGenerator(unittest.TestCase):

    def setUp(self) -> None:
        os.environ['RDB_DATABASE_NAME'] = 'test_db'
        self.generator = SnowflakeTaskGenerator()  # type: ignore
        self.maxDiff = None

    def tearDown(self) -> None:
        os.environ.pop('RDB_DATABASE_NAME')

    def test_get_conn_str(self) -> None:
        expected = 'snowflake://user_name:password@account/?warehouse=warehouse'
        actual = self.generator.get_conn_string()
        self.assertEqual(actual, expected)
