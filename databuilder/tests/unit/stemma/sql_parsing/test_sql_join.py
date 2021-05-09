# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import unittest

from databuilder.stemma.sql_parsing.sql_join import SqlJoin


class TestSqlWhere(unittest.TestCase):

    def test_set_join_type(self) -> None:
        sj1 = SqlJoin(left_table=None, right_table=None, join_type='join', join_operator=None, join_sql=None)
        self.assertEqual(sj1.join_type, 'inner join')

        sj2 = SqlJoin(left_table=None, right_table=None, join_type='left join', join_operator=None, join_sql=None)
        self.assertEqual(sj2.join_type, 'left join')

