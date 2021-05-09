# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.stemma.sql_parsing.sql_table import SqlTable
from databuilder.stemma.sql_parsing.sql_where import WhereClause

from . import DEFAULT_CLUSTER, DEFAULT_DATABASE, DEFAULT_SCHEMA


DEFAULT_ALIASES = {
    'a': 'ca_covid.open_data.statewide_testing',
    'b': 'ca_covid.open_data.statewide_cases'
}


class TestWhereClause(unittest.TestCase):

    def test_filter_tables(self) -> None:
        tbl_a = SqlTable(table_reference=DEFAULT_ALIASES['a'], default_cluster='', default_schema='')
        tbl_b = SqlTable(table_reference=DEFAULT_ALIASES['b'], default_cluster='', default_schema='')

        full_clause = 'b.newcountdeaths <= 15'
        wc = WhereClause(tables=[tbl_a, tbl_b], aliases=DEFAULT_ALIASES, full_clause=full_clause,
                           left_arg=None, right_arg=None, operator=None)
        # Table 'a' not referenced in where clause
        self.assertEqual(wc.tables, [tbl_b])

    def test_build_aliases(self) -> None:
        wc = WhereClause(tables=[], aliases=DEFAULT_ALIASES, full_clause='',
                           left_arg=None, right_arg=None, operator=None,
                           default_database=DEFAULT_DATABASE, default_schema=DEFAULT_SCHEMA)

        full_alias_name = 'my_db_name.my_schema_name.my_table_name'
        full_alias = wc._build_alias_with_defaults(full_alias_name)
        self.assertEqual(full_alias, full_alias_name)

        missing_db_name = 'my_schema_name.my_table_name'
        alias_no_db = wc._build_alias_with_defaults(missing_db_name)
        self.assertEqual(alias_no_db, f'{DEFAULT_DATABASE}.{missing_db_name}')

        alias_no_db_schema_name = 'my_table_name'
        alias_no_db_schema = wc._build_alias_with_defaults(alias_no_db_schema_name)
        self.assertEqual(alias_no_db_schema, f'{DEFAULT_DATABASE}.{DEFAULT_SCHEMA}.{alias_no_db_schema_name}')


