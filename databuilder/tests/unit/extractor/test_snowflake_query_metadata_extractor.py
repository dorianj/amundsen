# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import datetime as dt
import logging
import unittest

from mock import MagicMock, patch
from pyhocon import ConfigFactory

from databuilder.extractor.snowflake_query_metadata_extractor import SnowflakeQueryMetadataExtractor
from databuilder.extractor.sql_alchemy_extractor import SQLAlchemyExtractor
from databuilder.models.query import (
    QueryExecutionsMetadata, QueryJoinMetadata, QueryMetadata, QueryWhereMetadata,
)
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.stemma.sql_parsing.sql_parsing import SqlParser


class TestSnowflakeQueryMetadataExtractor(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.maxDiff = None
        _dt = dt.datetime(2021, 5, 1, 0, 0, 0)
        yest_day = (_dt - dt.timedelta(days=1)).date().strftime('%Y-%m-%d')
        today = _dt.strftime('%Y-%m-%d %H:%M:%S')
        config_dict = {
            # These values are not getting used?? Why are the values in the default dict in the class used?
            f'extractor.sqlalchemy.{SQLAlchemyExtractor.CONN_STRING}': 'TEST_CONNECTION',
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.DATABASE_KEY}': 'snowflake',
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.SNOWFLAKE_DATABASE_KEY}': 'prod',
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.DEFAULT_SCHEMA_KEY}': 'DEFAULT',
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.START_TIMESTAMP}': yest_day,
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.END_TIMESTAMP}': today,
            f'extractor.snowflake_query_metadata.{SnowflakeQueryMetadataExtractor.FETCH_SIZE}': 20
        }
        self.conf = ConfigFactory.from_dict(config_dict)

    def test_extraction_with_empty_query_result(self) -> None:
        """
        Test Extraction with empty result from query
        """
        with patch.object(SQLAlchemyExtractor, '_get_connection'):
            extractor = SnowflakeQueryMetadataExtractor()
            extractor.init(self.conf)

            results = extractor.extract()
            self.assertEqual(results, None)

    def test_extraction_with_filter(self) -> None:
        with patch.object(SQLAlchemyExtractor, '_get_connection') as mock_connection:
            connection = MagicMock()
            mock_connection.return_value = connection
            sql_execute = MagicMock()
            connection.execute = sql_execute
            sql_execute.return_value = [
                {
                    'query_id': '123',
                    'database_name': 'some_snowflake_db',
                    'schema_name': 'test_schema1',
                    'query_text': 'select field1, field2 from test_table1 where field1 > 3',
                    'user_name': 'user_name',
                    'start_time': dt.datetime(2021, 5, 8, 17, 30, 38, 26000),
                    'end_time': dt.datetime(2021, 5, 8, 17, 30, 38, 26000)
                }
            ]

            # Mock SQL Parser results
            with patch.object(SqlParser, '_post') as mock_post:
                mock_post.side_effect = [
                    {
                        'tables': ['test_table1'],
                        'aliases': {'test_table1': 'test_table1'},
                        'clean_sql': 'select field1, field2 from test_table1 where field1 > 3',
                        'fields': ['test_table1.field1', 'test_table1.field2']
                    },
                    {
                        'wheres': [
                            {
                                'tables': {'test_table1': 'test_table1'},
                                'full_clause': 'field1 > 3',
                                'operator': '>',
                                'right_arg': '3',
                                'left_arg': 'field1'
                            }
                        ]
                    },
                    {'joins': []}
                ]

                extractor = SnowflakeQueryMetadataExtractor()
                extractor.init(self.conf)
                actual_query = extractor.extract()

                table_metadata = TableMetadata(
                    'snowflake',
                    'some_snowflake_db',
                    'test_schema1',
                    'test_table1',
                    'test_table1',
                    [
                        ColumnMetadata('field1', 'desc', 'bigint', 0),
                        ColumnMetadata('field2', 'description', 'bigint', 1)
                    ]
                )
                # Query
                expected_query = QueryMetadata(sql='select field1, field2 from test_table1 where field1 > 3',
                                               tables=[table_metadata])

                self.assertEqual(expected_query.__repr__(), actual_query.__repr__())

                # Query Where
                actual_where = extractor.extract()
                expected_where = QueryWhereMetadata(tables=[table_metadata],
                                                    where_clause='field1 > 3',
                                                    left_arg='field1',
                                                    right_arg='3',
                                                    operator='>',
                                                    alias_mapping=dict(),
                                                    query_metadata=expected_query)
                self.assertEqual(actual_where.__repr__(), expected_where.__repr__())

                # Query Execution
                actual_execution = extractor.extract()
                expected_execution = QueryExecutionsMetadata(expected_query,
                                                             start_time=1619838000000,
                                                             execution_count=1)
                self.assertEqual(actual_execution.__repr__(), expected_execution.__repr__())

    def test_extraction_with_join(self) -> None:
        with patch.object(SQLAlchemyExtractor, '_get_connection') as mock_connection:
            connection = MagicMock()
            mock_connection.return_value = connection
            sql_execute = MagicMock()
            connection.execute = sql_execute

            sql_string = 'select field1, field2 from test_table1 a join table2 b on a.a = b.a'
            sql_execute.return_value = [
                {
                    'query_id': '123',
                    'database_name': 'some_snowflake_db',
                    'schema_name': 'test_schema1',
                    'query_text': sql_string,
                    'user_name': 'user_name',
                    'start_time': dt.datetime(2021, 5, 8, 17, 30, 38, 26000),
                    'end_time': dt.datetime(2021, 5, 8, 17, 30, 38, 26000)
                }
            ]
            with patch.object(SqlParser, '_post') as mock_post:
                mock_post.side_effect = [
                    {
                        'tables': ['table2', 'test_table1'],
                        'aliases': {'a': 'test_table1', 'b': 'table2'},
                        'clean_sql': 'select field1, field2 from test_table1 a join table2 b on a.a = b.a',
                        'fields': ['missed.field1(1,8)', 'missed.field2(1,16)', 'table2.a', 'test_table1.a']
                    },
                    {'wheres': []},
                    {
                        'joins': [
                            {
                                'right_column': 'a',
                                'join_sql': 'test_table1 a join table2 b on a.a = b.a',
                                'right_table': 'table2',
                                'join_type': 'join',
                                'left_table': 'test_table1',
                                'join_operator': '=',
                                'left_column': 'a'
                            }
                        ]
                    }
                ]

                extractor = SnowflakeQueryMetadataExtractor()
                extractor.init(self.conf)
                actual_query = extractor.extract()

                left_col = ColumnMetadata('a', 'desc', 'bigint', 0)
                left_table = TableMetadata(
                    'snowflake',
                    'some_snowflake_db',
                    'test_schema1',
                    'test_table1',
                    'test_table1',
                    [left_col]
                )
                right_col = ColumnMetadata('a', 'desc', 'bigint', 0)
                right_table = TableMetadata(
                    'snowflake',
                    'some_snowflake_db',
                    'test_schema1',
                    'table2',
                    'table2',
                    [right_col]
                )
                # Query
                expected_query = QueryMetadata(sql=sql_string,
                                               tables=[right_table, left_table])

                self.assertEqual(expected_query.__repr__(), actual_query.__repr__())

                # Query Join
                actual_join = extractor.extract()
                expected_join = QueryJoinMetadata(left_table=left_table,
                                                  right_table=right_table,
                                                  left_column=left_col,
                                                  right_column=right_col,
                                                  join_type='inner join',
                                                  join_operator='=',
                                                  join_sql='a.a = b.a',
                                                  query_metadata=expected_query)
                self.assertEqual(actual_join.__repr__(), expected_join.__repr__())

                # Query Execution
                actual_execution = extractor.extract()
                expected_execution = QueryExecutionsMetadata(expected_query,
                                                             start_time=1619838000000,
                                                             execution_count=1)
                self.assertEqual(actual_execution.__repr__(), expected_execution.__repr__())
