# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest
from unittest import mock
from unittest.mock import MagicMock

from databuilder.stemma.sql_parsing.sql_parsing import SqlParser
from databuilder.stemma.sql_parsing.sql_join import SqlJoin
from databuilder.stemma.sql_parsing.sql_table import SqlTable
from databuilder.stemma.sql_parsing.sql_where import WhereClause



class TestSqlParsing(unittest.TestCase):

    def setUp(self) -> None:
        sp = SqlParser(host='', database_type='', sql='', default_database_name='',
                       default_schema_name='')
        self.default_sql_parser = sp

    def test_default_clean(self) -> None:

        sp = SqlParser(host='', database_type='', sql='', default_database_name='',
                       default_schema_name='', clean_data=True, clean_chars=['`', '"'])

        dirty_string = 'AB`CD"EF`GH""'
        clean_string = sp._default_clean(dirty_string)
        self.assertEqual(clean_string, 'abcdefgh')

        sp2 = SqlParser(host='', database_type='', sql='', default_database_name='',
                        default_schema_name='', clean_data=False, clean_chars=['`', '"'])

        dirty_string = 'AB`CD"EF`GH""'
        clean_string = sp2._default_clean(dirty_string)
        self.assertEqual(clean_string, dirty_string)

    def test_clean_dict(self) -> None:
        sp = SqlParser(host='', database_type='', sql='', default_database_name='',
                       default_schema_name='', clean_chars=['`', '!', '"'])

        d = {
            'field1': 'ABC`FEGH""',
            'field2': {
                'field2_a': 'IjK`!MN'
            },
            'field3': ['OP`qR"'],
            'field4': {
                'field_4a': [{'field_4a_1': "StU3!`"}],
                'field_4b': 'VWx!yZ`'
            }
        }
        cleaned = sp._clean_dict(d)
        expected = {
            'field1': 'abcfegh',
            'field2': {
                'field2_a': 'ijkmn'
            },
            'field3': ['opqr'],
            'field4': {
                'field_4a': [{'field_4a_1': "stu3"}],
                'field_4b': 'vwxyz'
            }
        }
        self.assertEqual(cleaned, expected)

    def test_is_valid_table_col_resp(self) -> None:
        resp_val = {'tables': ['some_val'], 'fields': ['something']}
        valid_resp = self.default_sql_parser._is_valid_table_col_resp(resp_val)
        self.assertTrue(valid_resp)

        invalid_resp_val1 = {'fields': ['something']}
        invalid_resp1 = self.default_sql_parser._is_valid_table_col_resp(invalid_resp_val1)
        self.assertFalse(invalid_resp1)

        invalid_resp_val2 = {'tables': ['something']}
        invalid_resp2 = self.default_sql_parser._is_valid_table_col_resp(invalid_resp_val2)
        self.assertFalse(invalid_resp2)

    def test_is_valid_table_join_resp(self) -> None:
        resp_val = {'joins': ['some_val']}
        valid_resp = self.default_sql_parser._is_valid_table_join_resp(resp_val)
        self.assertTrue(valid_resp)

        invalid_resp_val1 = {'fields': ['something']}
        invalid_resp1 = self.default_sql_parser._is_valid_table_join_resp(invalid_resp_val1)
        self.assertFalse(invalid_resp1)

    def test_is_valid_table_where_resp(self) -> None:
        resp_val = {'wheres': ['some_val']}
        valid_resp = self.default_sql_parser._is_valid_table_where_resp(resp_val)
        self.assertTrue(valid_resp)

        invalid_resp_val1 = {'fields': ['something']}
        invalid_resp1 = self.default_sql_parser._is_valid_table_where_resp(invalid_resp_val1)
        self.assertFalse(invalid_resp1)


    def test_is_valid_lineage_resp(self) -> None:
        resp_val = {'dbobjs': ['some_val'], 'relations': ['something']}
        valid_resp = self.default_sql_parser._is_valid_lineage_resp(resp_val)
        self.assertTrue(valid_resp)

        invalid_resp_val1 = {'dbobjs': ['something']}
        invalid_resp1 = self.default_sql_parser._is_valid_lineage_resp(invalid_resp_val1)
        self.assertFalse(invalid_resp1)

        invalid_resp_val2 = {'relations': ['something']}
        invalid_resp2 = self.default_sql_parser._is_valid_lineage_resp(invalid_resp_val2)
        self.assertFalse(invalid_resp2)

    def test_assign_cols_to_table(self) -> None:
        tbl = SqlTable(table_reference='table', default_cluster='', default_schema='')
        tbl2 = SqlTable(table_reference='table2', default_cluster='', default_schema='')
        self.default_sql_parser._assign_cols_to_table(tables={'tbl1': tbl, 'tbl2': tbl2},
                                                      columns=['tbl1.col1', 'tbl2.col2'])
        self.assertEqual(tbl.columns, ['col1'])
        self.assertEqual(tbl2.columns, ['col2'])

    def test_clean_join(self) -> None:
        join_input = {
            'right_column': 'tested',
            'join_sql': '''
                STATEWIDE_CASES cases
                join  STATEWIDE_TESTING tests on cases.newcountconfirmed <= tests.tested
            ''',
            'right_table': 'STATEWIDE_TESTING',
            'join_type': 'join',
            'left_table': 'STATEWIDE_CASES',
            'join_operator': '<=',
            'left_column':
            'newcountconfirmed'
        }
        joins = self.default_sql_parser._clean_joins([join_input])
        self.assertTrue(isinstance(joins[0], SqlJoin))
        self.assertEqual(joins[0].left_table.table, 'statewide_cases')
        self.assertEqual(joins[0].right_table.table, 'statewide_testing')
        self.assertEqual(joins[0].join_type, 'inner join')

    def test_clean_wheres(self) -> None:
        where_input = {
            'tables': {
                'a': '"ca_covid"."OPEN_DATA"."STATEWIDE_TESTING"',
                'b': '"ca_covid"."OPEN_DATA"."STATEWIDE_CASES"'
            },
            'full_clause': 'a.tested <= b.totalcountconfirmed * 100',
            'operator': '<=',
            'right_arg': 'b.totalcountconfirmed * 100',
            'left_arg': 'a.tested'
        }
        wheres = self.default_sql_parser._clean_wheres([where_input])
        self.assertTrue(all([isinstance(x, WhereClause) for x in wheres]))
        tbl_names = ['statewide_testing', 'statewide_cases']
        for tbl in wheres[0].tables:
            self.assertTrue(tbl.table in tbl_names)

    @mock.patch('databuilder.stemma.sql_parsing.sql_parsing.SqlParser._post')
    def test_get_tables_columns(self, mock_post_proxy_client: MagicMock) -> None:
        response = {
            'tables': ['STATEWIDE_CASES', 'STATEWIDE_TESTING'],
            'aliases': {'cases': 'STATEWIDE_CASES', 'tests': 'STATEWIDE_TESTING'},
            'clean_sql': '''
                select *
                from  STATEWIDE_CASES cases
                join  STATEWIDE_TESTING tests on cases.newcountconfirmed <= tests.tested
                ;
            ''',
            'fields': [
                'STATEWIDE_CASES.*',
                'STATEWIDE_CASES.newcountconfirmed',
                'STATEWIDE_TESTING.*',
                'STATEWIDE_TESTING.tested'
            ]
        }
        mock_post_proxy_client.return_value = response

        tbls_cols = self.default_sql_parser.get_tables_columns()
        expected_tables_cols = {
            'statewide_testing': {
                'columns': ['*', 'tested'],
                'schema': '',  # defaults are set to empty string
                'cluster': ''
            },
            'statewide_cases': {
                'columns': ['*', 'newcountconfirmed'],
                'schema': '',
                'cluster': ''
            }
        }
        for tbl in tbls_cols:
            self.assertTrue(isinstance(tbl, SqlTable))
            self.assertTrue(tbl.table in expected_tables_cols)
            self.assertEquals(tbl.columns, expected_tables_cols[tbl.table]['columns'])
            self.assertEquals(tbl.schema, expected_tables_cols[tbl.table]['schema'])
            self.assertEquals(tbl.cluster, expected_tables_cols[tbl.table]['cluster'])


    @mock.patch('databuilder.stemma.sql_parsing.sql_parsing.SqlParser._post')
    def test_get_tables_joins(self, mock_post_proxy_client: MagicMock) -> None:
        response = {
            'joins': [
                {
                    'right_column': 'tested',
                    'join_sql': '''
                        STATEWIDE_CASES cases
                        join  STATEWIDE_TESTING tests on cases.newcountconfirmed <= tests.tested
                    ''',
                    'right_table': 'STATEWIDE_TESTING',
                    'join_type': 'join',
                    'left_table': 'STATEWIDE_CASES',
                    'join_operator': '<=',
                    'left_column': 'newcountconfirmed'
                }
            ]
        }

        mock_post_proxy_client.return_value = response

        joins = self.default_sql_parser.get_tables_joins()
        expected_join = {
            'right_column': 'tested',
            'right_table': 'statewide_testing',
            'join_type': 'inner join',
            'left_table': 'statewide_cases',
            'operator': '<=',
            'left_column': 'newcountconfirmed'
        }
        self.assertEqual(len(joins), 1)
        self.assertTrue(isinstance(joins[0], SqlJoin))
        self.assertTrue(isinstance(joins[0], SqlJoin))
        self.assertEquals(joins[0].left_table.table, expected_join['left_table'])
        self.assertEquals(joins[0].right_table.table, expected_join['right_table'])
        self.assertEquals(joins[0].left_table.columns[0], expected_join['left_column'])
        self.assertEquals(joins[0].join_operator, expected_join['operator'])
        self.assertEquals(joins[0].right_table.columns[0], expected_join['right_column'])
        self.assertEquals(joins[0].join_type, expected_join['join_type'])


    @mock.patch('databuilder.stemma.sql_parsing.sql_parsing.SqlParser._post')
    def test_get_query_wheres(self, mock_post_proxy_client: MagicMock) -> None:
        response = {
            'wheres': [
                {
                    'tables': {
                        'a': '"ca_covid"."OPEN_DATA"."STATEWIDE_TESTING"',
                        'b': '"ca_covid"."OPEN_DATA"."STATEWIDE_CASES"'
                    },
                    'full_clause': 'a.tested <= b.totalcountconfirmed * 100',
                    'operator': '<=',
                    'right_arg': 'b.totalcountconfirmed * 100',
                    'left_arg':
                    'a.tested'
                },
                {
                    'tables': {
                        'a': '"ca_covid"."OPEN_DATA"."STATEWIDE_TESTING"',
                        'b': '"ca_covid"."OPEN_DATA"."STATEWIDE_CASES"'
                    }, 'full_clause': 'b.newcountdeaths <= 15',
                    'operator': '<=',
                    'right_arg':
                    '15',
                    'left_arg': 'b.newcountdeaths'
                }
            ]
        }
        mock_post_proxy_client.return_value = response

        wheres = self.default_sql_parser.get_query_wheres()
        expected_wheres = {
            'right_column': 'tested',
            'right_table': 'statewide_testing',
            'join_type': 'inner join',
            'left_table': 'statewide_cases',
            'operator': '<=',
            'left_column': 'newcountconfirmed'
        }
        self.assertEqual(len(wheres), 2)
        self.assertTrue([all(isinstance(w, WhereClause) for w in wheres)])

        where1_tables = ['statewide_testing', 'statewide_cases']
        self.assertEqual([tbl.table for tbl in wheres[0].tables], where1_tables)
        where2_tables = ['statewide_cases']
        self.assertEqual([tbl.table for tbl in wheres[1].tables], where2_tables)

        where1_aliases = {
            'ca_covid.open_data.statewide_cases': 'b',
            'ca_covid.open_data.statewide_testing': 'a'
        }
        self.assertEqual(wheres[0].aliases, where1_aliases)
        where2_aliases = {
            'ca_covid.open_data.statewide_cases': 'b',
            'ca_covid.open_data.statewide_testing': 'a'
        }
        self.assertEqual(wheres[1].aliases, where2_aliases)
