import functools
from typing import (
    Any, Dict, List, Optional,
)

import requests as r

from databuilder.stemma.sql_parsing.gsp_enums import GSP_JOIN_ENUM_STR_MAP, GSPJoinType
from databuilder.stemma.sql_parsing.sql_join import SqlJoin
from databuilder.stemma.sql_parsing.sql_table import SqlTable
from databuilder.stemma.sql_parsing.sql_where import WhereClause

TABLE_COLUMNS_ENDPOINT = '/parse-tables-columns'
JOINS_ENDPOINT = '/parse-joins'
LINEAGE_ENDPOINT = '/parse-lineage'
WHERES_ENDPOINT = '/parse-wheres'

# Characters to remove from table and column names
# TODO: should this be more generic and deeply engrainged
#   within Amundsen???
DEFAULT_REMOVE_CHARS = ['`', '"']


class InvalidGspResponse(Exception):
    pass


class SqlParser(object):
    """
    This class is responsible for ser/de with the Stemma SQL Parser API. It will
    invoke the API, retrieve results, format results, cleanse data and make
    objects available to clients with the shape and semantics that are conducive
    to building Databuilder objects.
    """
    def __init__(
        self,
        host: str,
        database_type: str,
        sql: str,
        default_database_name: str,
        default_schema_name: str = 'PUBLIC',
        clean_data: bool = True,
        clean_chars: List[str] = DEFAULT_REMOVE_CHARS
    ) -> None:
        """
        Constructor for `SqlParser`. Converts responses from the General SQL Parser (GSP)
        REST API wrapper into Databuilder serialized models.
        :param host: Host for the GSP REST wrapper
        :param database_type: Type of database the GSP should use to parse the query, GSP
            uses to select the correct dialict for parsing
        :param default_database_name: The default name of the database to use when the name
            of the database is not referenced in the SQL code for a given field / table. For
            example, a user may reference a table like: `... from database.schema.table` or
            they may use a syntax that does not require the database (e.g. `schema.table` or
            `table`). In the cases when the database is not available this default is applied.
            Note - many databases use the term "database" but in Amundsen it is often called
            "cluster", here the "default_database_name" is the Amundsen "cluster".
        :param default_schema_name: Default name of the schema to apply when it does not exist.
            See `default_database_name` for full details.
            TODO: Users can actually change schemas and it will not come through in the SQL code
                For example, the following queries in order:
                    - Select * from schema.table;
                    - use schema new_schema;
                    - select * from table;
                Both of these reference "table" but they are in different schemas.
        """
        # REST API attributes
        self.host = host[:-1] if host.endswith('/') else host
        self.database_type = database_type
        self.sql = sql
        self.clean_sql = None
        self.body = {'database': self.database_type, 'sql': self.sql}
        self.headers = {'Content-Type': 'application/json'}
        self._table_column_endpoint = self.host + TABLE_COLUMNS_ENDPOINT
        self._joins_endpoint = self.host + JOINS_ENDPOINT
        self._lineage_endpoint = self.host + LINEAGE_ENDPOINT
        self._wheres_endpoint = self.host + WHERES_ENDPOINT

        # Data cleaning attributes
        self.clean_chars = clean_chars
        self.clean_data = clean_data

        # Defaults
        self.default_database_name = self._default_clean(default_database_name)
        self.default_schema_name = self._default_clean(default_schema_name)

    def _post(self, endpoint: str) -> Dict:
        """
        Simple POST handler for interacting with SQL parsing server
        """
        return r.post(endpoint, json=self.body, headers=self.headers).json()

    def _default_clean(self, item: str) -> str:
        """
        Applies the generic cleaning of a field if required. Will change a value such as:
            `ca_covid`."OPEN_DATA"."STATEWIDE_TESTING"
        To
            ca_covid.open_data.statewide_testing
        """
        if self.clean_data:
            item = functools.reduce(lambda x, y: x.replace(y, ''), self.clean_chars, item).lower()
        return item

    def _clean_dict(self, input_d: Any) -> Any:
        """
        Attempts to clean each item in a dictionary. Converts all items to string.
        """
        if isinstance(input_d, str):
            return self._default_clean(input_d)

        new_d = {}
        for k, v in input_d.items():
            if isinstance(v, list):
                new_d[k] = [self._clean_dict(vi) for vi in v]
            elif isinstance(v, dict):
                new_d[k] = self._clean_dict(v)
            else:
                new_d[k] = self._default_clean(v)  # type: ignore
        return new_d

    def _is_valid_table_col_resp(self, resp: Dict) -> bool:
        """
        Checks whether or not the response for table/columns is valid
        """
        return isinstance(resp, dict) and 'tables' in resp and 'fields' in resp

    def _is_valid_table_join_resp(self, resp: Dict) -> bool:
        """
        Checks whether or not the response for table joins is valid
        """
        return isinstance(resp, dict) and 'joins' in resp

    def _is_valid_table_where_resp(self, resp: Dict) -> bool:
        """
        Checks whether or not the response for table wheres is valid
        """
        return isinstance(resp, dict) and 'wheres' in resp

    def _is_valid_lineage_resp(self, resp: Dict) -> bool:
        """
        Checks whether or not the response for lineage endpoint is valid
        """
        return isinstance(resp, dict) and 'dbobjs' in resp and 'relations' in resp

    def _assign_cols_to_table(self, tables: Dict[str, SqlTable], columns: List[str]) -> None:
        """
        Associates a list of columns to a corresponding SqlTable object.
        """
        for table_key, sql_table in tables.items():
            remaining_cols = []
            for col in columns:
                if col.startswith(table_key):
                    tbl_start = table_key + '.'
                    sql_table.columns.append(col.replace(tbl_start, ''))
                else:
                    remaining_cols.append(col)
            columns = remaining_cols

    def _clean_joins(self, joins: List[Dict]) -> List[SqlJoin]:
        """
        Cleans the values in the joins response and formats the join type.
        """
        join_results = []
        for join in joins:
            join = self._clean_dict(join)
            left_table = SqlTable(
                table_reference=join['left_table'],
                default_cluster=self.default_database_name,
                default_schema=self.default_schema_name
            )
            left_table.columns.append(join['left_column'])

            right_table = SqlTable(
                table_reference=join['right_table'],
                default_cluster=self.default_database_name,
                default_schema=self.default_schema_name
            )
            right_table.columns.append(join['right_column'])

            sql_join = SqlJoin(
                left_table=left_table,
                right_table=right_table,
                join_type=GSP_JOIN_ENUM_STR_MAP[GSPJoinType(join['join_type'])],
                join_operator=join['join_operator'],
                join_sql=join['join_sql']
            )
            join_results.append(sql_join)
        return join_results

    def _clean_wheres(self, wheres: List[Dict]) -> List[WhereClause]:
        """
        Cleans the values in the wheres response and formats the where type.
        """
        where_results: List[WhereClause] = []
        for where in wheres:
            where = self._clean_dict(where)
            tables = []
            for alias, table in where['tables'].items():
                t = SqlTable(
                    table_reference=table,
                    default_cluster=self.default_database_name,
                    default_schema=self.default_schema_name
                )
                # Add columns from the where clause to the table
                for potential_col in where['full_clause'].split(' '):
                    alias_id = alias + '.'

                    if potential_col.startswith(alias_id):
                        t.columns.append(potential_col.replace(alias_id, ''))

                t.columns = list(set(t.columns))
                tables.append(t)

            where_clause = WhereClause(tables=tables,
                                       aliases=where['tables'],
                                       left_arg=where['left_arg'],
                                       operator=where['operator'],
                                       right_arg=where['right_arg'],
                                       full_clause=where['full_clause'],
                                       default_database=self.default_database_name,
                                       default_schema=self.default_schema_name)
            where_results.append(where_clause)

        return where_results

    def get_clean_sql(self) -> str:
        # Clean SQL is retrieved from the tables / columns API. Force that data to be created / cached
        self.get_tables_columns()
        if self.clean_sql is not None:
            return self.clean_sql
        return self.sql

    def get_tables_columns(self) -> List[SqlTable]:
        """
        Returns a list of tables and columns used in a given query.
        Response format is
            >>> {
            >>>     'ca_covid.open_data.statewide_cases': ['date', 'newcountconfirmed']
            >>> }
        """
        if not hasattr(self, 'table_columns'):
            resp = self._post(self._table_column_endpoint)
            if self._is_valid_table_col_resp(resp):
                self.clean_sql = resp['clean_sql']
                tables = {}
                for table in resp['tables']:
                    table_key = self._default_clean(table)
                    sql_table = SqlTable(
                        table_reference=table_key,
                        default_cluster=self.default_database_name,
                        default_schema=self.default_schema_name
                    )
                    tables[table_key] = sql_table
                columns = [self._default_clean(c) for c in resp['fields']]
                self._assign_cols_to_table(tables=tables, columns=columns)
                self.table_columns = list(tables.values())
            else:
                raise InvalidGspResponse('The General SQL Parser response was not valid. Contained values: %s' % resp)
        return self.table_columns

    def get_tables_joins(self) -> List[SqlJoin]:
        """
        Returns a dictionary of tables and columns used in a given query.
        Response format is
            >>> {
            >>>        'joins': [
            >>>             {
            >>>                 'right_column': 'date',
            >>>                 'right_table': 'ca_covid.open_data.statewide_cases',
            >>>                 'join_type': 'join',
            >>>                 'left_table': 'ca_covid.open_data.statewide_testing',
            >>>                 'join_operator': '=',
            >>>                 'left_column': 'date'
            >>>                 'join_sql': 'table_1 t join table_2 t2 on t2.a = t.a',
            >>>                 'where_sql': ['where t.a > 30'],
            >>>             }
            >>>         ]
            >>>     }
        """
        if not hasattr(self, 'table_joins'):
            resp = self._post(self._joins_endpoint)
            if self._is_valid_table_join_resp(resp):
                self.table_joins = self._clean_joins(resp['joins'])
            else:
                raise InvalidGspResponse('The General SQL Parser response was not valid. Contained values: %s' % resp)
        return self.table_joins

    def get_query_wheres(self) -> List[WhereClause]:
        """
        Returns a dictionary of where clauses used in a given query.
        The column values provided have been curated to be as "fully
        qualified" as possible. That is, if the table is written as
        `... from db.schema.table as t ...` and the where clause is
        simply `where t.col = 1`. Then the column value in the response
        here will be `db.schema.table.col`.
            >>> {
            >>>     "wheres": [
            >>>         {
            >>>             "full_clause": "t.b > 30",
            >>>             "left_arg": "t.b",
            >>>             "tables": {
            >>>                 "t": "db.schema.table_1",
            >>>                 "t2":"db.schema.table2"
            >>>             }
            >>>             "right_arg": "30",
            >>>             "operator": ">"
            >>>         },
            >>>         {
            >>>             "full_clause": "a is not null",
            >>>             "left_arg": "a",
            >>>             "tables": {"table_1": "table_1"},
            >>>             "right_arg": "null",
            >>>             "operator": "not"
            >>>         }
            >>>     ]
            >>> }
        """
        if not hasattr(self, 'query_wheres'):
            resp = self._post(self._wheres_endpoint)
            if self._is_valid_table_where_resp(resp):
                self.query_wheres = self._clean_wheres(resp['wheres'])
            else:
                raise InvalidGspResponse('The General SQL Parser response was not valid. Contained values: %s' % resp)
        return self.query_wheres

    def get_lineage(self) -> Optional[Dict]:
        """
        Returns a dictionary of lineage
        """
        # TODO - this whole function needs to be done

        if not hasattr(self, 'lineage'):
            resp = self._post(self._lineage_endpoint)
            if self._is_valid_lineage_resp(resp):
                self.lineage = None
                pass
                # self.table_joins = [self._clean_dict(j) for j in resp['joins']]
            else:
                raise InvalidGspResponse('The General SQL Parser response was not valid. Contained values: %s' % resp)
        return self.lineage
