# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.stemma.sql_parsing.sql_join import SqlJoin
from databuilder.stemma.sql_parsing.sql_table import SqlTable


class TestSqlWhere(unittest.TestCase):

    def test_set_join_type(self) -> None:
        tbl = SqlTable('', '', '')
        sj1 = SqlJoin(left_table=tbl, right_table=tbl, join_type='join', join_operator='', join_sql='')
        self.assertEqual(sj1.join_type, 'inner join')

        sj2 = SqlJoin(left_table=tbl, right_table=tbl, join_type='left join', join_operator='', join_sql='')
        self.assertEqual(sj2.join_type, 'left join')
