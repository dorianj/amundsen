
from databuilder.stemma.sql_parsing.sql_table import SqlTable


class SqlJoin(object):
    def __init__(self, left_table: SqlTable, right_table: SqlTable, join_type: str,
                 join_operator: str, join_sql: str
                 ):
        self.left_table = left_table
        self.right_table = right_table
        # Force to "inner join" for normal "joins" to be more explicit
        self.join_type = 'inner join' if join_type == 'join' else join_type
        self.join_operator = join_operator
        self.join_sql = join_sql
