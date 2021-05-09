from typing import Dict, List

from databuilder.stemma.sql_parsing.sql_table import SqlTable


class WhereClause(object):
    def __init__(self, tables: List[SqlTable], aliases: Dict[str, str], left_arg: str, operator: str,
                 right_arg: str, full_clause: str, default_schema: str = None, default_database: str = None) -> None:
        # The default response from the API is all tables available scoped query, which could be a superset
        # of the tables for this specific clause. This filters by only mathcing the tables for this clause.
        if len(tables) == 1:
            self.tables = tables
        else:
            self.tables = self._filter_tables(tables=tables, aliases=aliases, full_clause=full_clause)

        self.default_schema = default_schema
        self.default_database = default_database
        self.aliases = {self._build_alias_with_defaults(v): k for k, v in aliases.items()}
        self.left_arg = left_arg
        self.operator = operator
        self.right_arg = right_arg
        self.full_clause = full_clause

    def _build_alias_with_defaults(self, alias) -> str:
        alias_resp = alias
        alias_split = alias.split('.')
        if len(alias_split) == 3:
            pass
        elif len(alias_split) == 2 and self.default_database is not None:
            alias_resp = f'{self.default_database}.{alias}'
        elif len(alias_split) == 1:
            if self.default_database is None and self.default_schema is not None:
                alias_resp = f'{self.default_schema}.{alias}'
            elif self.default_database is not None and self.default_schema is not None:
                alias_resp = f'{self.default_database}.{self.default_schema}.{alias}'
        return alias_resp

    def _filter_tables(self, tables: List[SqlTable], aliases: Dict[str, str], full_clause: str) -> List[SqlTable]:
        """
        Filters the list of all tables to the list of tables used in a specific where clause. Checks to
        see if the table name or the table alias exists within the where clause.
        """
        full_clause_lwr = full_clause.lower()

        found_tables = []
        for sql_t in tables:
            tbl_name = sql_t.table.lower() + '.'
            alias_name = 'n/a'
            for alias, alias_tbl_name in aliases.items():
                if alias_tbl_name.endswith('.' + sql_t.table.lower()):
                    alias_name = alias + '.'
                    continue

            if tbl_name in full_clause_lwr or alias_name in full_clause_lwr:
                found_tables.append(sql_t)
                continue

        return found_tables
