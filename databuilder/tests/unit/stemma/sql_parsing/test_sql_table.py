# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.stemma.sql_parsing.sql_table import SqlTable

from . import DEFAULT_CLUSTER, DEFAULT_SCHEMA


class TestSqlJoin(unittest.TestCase):

    def test_set_values(self) -> None:

        tbl = SqlTable(table_reference='my_table', default_cluster=DEFAULT_CLUSTER, default_schema=DEFAULT_SCHEMA)
        self.assertEqual(tbl.cluster, DEFAULT_CLUSTER)
        self.assertEqual(tbl.schema, DEFAULT_SCHEMA)
        self.assertEqual(tbl.table, 'my_table')

        schema_tbl = SqlTable(table_reference='my_schema.my_table',
                              default_cluster=DEFAULT_CLUSTER,
                              default_schema=DEFAULT_SCHEMA)
        self.assertEqual(schema_tbl.cluster, DEFAULT_CLUSTER)
        self.assertEqual(schema_tbl.schema, 'my_schema')
        self.assertEqual(schema_tbl.table, 'my_table')

        clster_schema_tbl = SqlTable(table_reference='my_cluster.my_schema.my_table',
                                     default_cluster=DEFAULT_CLUSTER, default_schema=DEFAULT_SCHEMA)
        self.assertEqual(clster_schema_tbl.cluster, 'my_cluster')
        self.assertEqual(clster_schema_tbl.schema, 'my_schema')
        self.assertEqual(clster_schema_tbl.table, 'my_table')
