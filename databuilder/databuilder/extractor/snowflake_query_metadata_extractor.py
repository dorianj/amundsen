# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import datetime as dt
import logging
from collections import namedtuple
from itertools import groupby
from typing import (
    Any, Dict, Iterator, List, Union,
)

from pyhocon import ConfigFactory, ConfigTree
from unidecode import unidecode

from databuilder.extractor import sql_alchemy_extractor
from databuilder.extractor.base_extractor import Extractor
from databuilder.models.query import (
    QueryExecutionsMetadata, QueryJoinMetadata, QueryMetadata, QueryWhereMetadata
)
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.models.user import User as UserMetadata
from databuilder.stemma.sql_parsing.sql_parsing import SqlParser
from databuilder.stemma.sql_parsing.sql_table import SqlTable
from databuilder.stemma.sql_parsing.sql_join import SqlJoin
from databuilder.stemma.sql_parsing.sql_where import WhereClause


LOGGER = logging.getLogger(__name__)


class InvalidSnowflakeTimestamp(Exception):
    pass


class SnowflakeQueryMetadataExtractor(Extractor):
    """
    Extracts Snowflake query metadata including:
        - Table table usage statistics
        - Frequent users
    In the future can be used to extract lineage.
    Snowflake query history docs:
    https://docs.snowflake.com/en/sql-reference/account-usage/query_history.html
    Requirements:
        snowflake-connector-python
        snowflake-sqlalchemy
    """

    # TODO
    # - limit by user
    # - limit by database
    SQL_STATEMENT = """
        SELECT
            query_id,
            database_name,
            schema_name,
            query_text,
            user_name
        FROM table(information_schema.query_history()) as query_history
        WHERE execution_status = 'SUCCESS'
              and query_history.START_TIME >= '{start_timestamp}'
              and query_history.START_TIME < '{end_timestamp}'
              and query_history.QUERY_TYPE in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')
              and query_history.DATABASE_NAME is not null
              and not CONTAINS(lower(query_history.QUERY_TEXT), 'information_schema')
              -- These queries are submitted by SqlAlchemy
              and query_history.QUERY_TEXT not in (
                  'ROLLBACK',
                  'SELECT CAST(''test unicode returns'' AS VARCHAR(60)) AS anon_1',
                  'SELECT CAST(''test plain returns'' AS VARCHAR(60)) AS anon_1'
                )
        ORDER BY query_history.START_TIME DESC, query_id ASC
        LIMIT {limit} OFFSET {offset}
        ;
    """

    ###############
    # Config Keys #
    ###############

    # Database Key, used to identify the database type in the UI.
    DATABASE_KEY = 'database_key'
    # Snowflake Database Key, used to determine which Snowflake database to connect to.
    SNOWFLAKE_DATABASE_KEY = 'snowflake_database'
    # The default schema is used to assign a schema to queries that do not have a schema prepended to the
    # table name.
    DEFAULT_SCHEMA_KEY = 'snowflake_schema'
    # Start and end timestamps used to pull queries. Must be in one of the following formats:
    #   'YYYY-MM-DD'           (e.g: datetime.datetime.now().strftime('%Y-%m-%d'))
    #   'YYYY-MM-DD HH:MM:SS'  (e.g: datetime.datetime.now().strftime('%Y-%m-%d %H:%M%S'))
    START_TIMESTAMP = 'start_timestamp'
    END_TIMESTAMP = 'end_timestamp'
    # Number of rows to fetch at a time
    FETCH_SIZE = 'fetch_size'
    # Host for the SQL Parser REST API
    SQL_PARSER_HOST = 'sql_parser_host'

    _defualt_dt = dt.datetime(2021, 5, 1, 0, 0, 0)
    DEFAULT_CONFIG = ConfigFactory.from_dict({
        DATABASE_KEY: 'snowflake',
        SNOWFLAKE_DATABASE_KEY: 'prod',
        DEFAULT_SCHEMA_KEY: 'PUBLIC',
        START_TIMESTAMP: _defualt_dt.strftime('%Y-%m-%d %H:%M:%S'),
        END_TIMESTAMP: (_defualt_dt - dt.timedelta(days=1)).date().strftime('%Y-%m-%d'),
        FETCH_SIZE: 1000,
        SQL_PARSER_HOST: 'http://localhost:8080'
    })

    ####################
    # Other Attributes #
    ####################
    SNOWFLAKE_DATE_FMT = '%Y-%m-%d'
    SNOWFLAKE_TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'
    VALID_TS_FORMATS = [SNOWFLAKE_DATE_FMT, SNOWFLAKE_TIMESTAMP_FMT]


    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(self.DEFAULT_CONFIG)
        self._conf = conf

        # Database configs
        self.database = conf.get_string(self.DATABASE_KEY)
        self.snowflake_database = conf.get_string(self.SNOWFLAKE_DATABASE_KEY)
        self.default_schema = conf.get_string(self.DEFAULT_SCHEMA_KEY)
        self.start_timestamp = self._try_load_timestamp(conf.get_string(self.START_TIMESTAMP))
        self.start_timestamp_millis = int(self.start_timestamp.timestamp() * 1000)
        self.end_timestamp = self._try_load_timestamp(conf.get_string(self.END_TIMESTAMP))

        # Set fetch and offset values
        self.fetch_size = conf.get_int(self.FETCH_SIZE)
        self.current_offset = 0

        # SQL Parser API configs
        self._sql_parser_host = conf.get_string(self.SQL_PARSER_HOST)

        # DB connection
        self._alchemy_extractor = None
        self._extract_iter: Union[None, Iterator] = None

    def close(self) -> None:
        self._try_close_connector()

    def _try_close_connector(self) -> None:
        if getattr(self, '_alchemy_extractor', None) is not None:
            self._alchemy_extractor.close()

    def extract(self) -> Union[TableMetadata, None]:
        if not self._extract_iter:
            self._create_query_metadata()
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return 'extractor.snowflake_query_metadata'

    def _try_load_timestamp(self, ts: str) -> dt.datetime:
        for ts_fmt in SnowflakeQueryMetadataExtractor.VALID_TS_FORMATS:
            try:
                return dt.datetime.strptime(ts, ts_fmt)
            except ValueError as ve:
                pass

        raise InvalidSnowflakeTimestamp(
            'The timestamp provided: %s does not match of of the required formats: %s', ts, SnowflakeQueryMetadataExtractor.VALID_TS_FORMATS
        )


    def _get_query_metadata(self, tables_columns: List[SqlTable], sql: str, clean_sql: str,
                            user: UserMetadata = None) -> QueryMetadata:
        """
        Converts a list of SqlTables (e.g. serialized response from the SQL Parsed API)
        to a Query Metadata object.
        """
        query_tables = []
        for table in tables_columns:
            tm = TableMetadata(
                database=self.database,
                cluster=table.cluster,
                schema=table.schema,
                name=table.table,
                description=None
            )
            query_tables.append(tm)

        return QueryMetadata(
            sql=sql,
            tables=query_tables,
            user=user,
            yield_relation_nodes=True,
            clean_sql=clean_sql
        )

    def _get_query_where_metadata(self, query_wheres: List[WhereClause],
                                        query_metadata: QueryMetadata = None) -> List[QueryWhereMetadata]:
        """
        Converts a list of Stemma `WhereClauses` into a list of `QueryWhereMetadata` models objects.
        """
        all_wheres = []
        for where in query_wheres:
            where_tables = []
            alias_mapping = {}
            for where_tbl in where.tables:
                where_tm = TableMetadata(
                    database=self.database,
                    cluster=where_tbl.cluster,
                    schema=where_tbl.schema,
                    name=where_tbl.table,
                    description=None,
                    columns=[
                        ColumnMetadata(name=where_col, description=None, col_type=None, sort_order=ind)
                        for ind, where_col in enumerate(where_tbl.columns)
                    ]
                )
                where_tables.append(where_tm)
                # The SQL Parser API attempts to add aliases if they do not exist. This creates a map of the alias
                # to the table metadata required to build hpyer link URLs in the frontend. Alises will be
                # replaced with the hyperlink table name
                alias_mapping[where_tbl.table_id] = {'alias': where.aliases[where_tbl.table_id], 'table': where_tbl}

            qw = QueryWhereMetadata(
                tables=where_tables,
                where_clause=where.full_clause,
                left_arg=where.left_arg,
                right_arg=where.right_arg,
                operator=where.operator,
                query_metadata=query_metadata,
                alias_mapping=alias_mapping,
                yield_relation_nodes=True
            )
            all_wheres.append(qw)
        return all_wheres

    def _get_query_join_metadata(self, table_joins: List[SqlJoin], query_metadata: QueryMetadata = None) -> List[QueryJoinMetadata]:
        """
        Converts a list of Stemma `SqlJoin` into a list of `QueryJoinMetadata` models objects.
        Optionally also associates the `QueryJoinMetadata` to a `QueryMetadata` object.
        """
        all_joins = []
        # The query join. Build table/column metadata for the keys
        for join in table_joins:
            # Left side of join
            left_cols_in_join = [
                ColumnMetadata(name=join.left_table.columns[0], description=None, col_type=None, sort_order=0)
            ]
            left_table_md = TableMetadata(
                database=self.database,
                cluster=join.left_table.cluster,
                schema=join.left_table.schema,
                name=join.left_table.table,
                description=None,
                columns=left_cols_in_join
            )

            # Right side of join
            right_cols_in_join = [
                ColumnMetadata(name=join.right_table.columns[0], description=None, col_type=None, sort_order=0)
            ]
            right_table_md = TableMetadata(
                database=self.database,
                cluster=join.right_table.cluster,
                schema=join.right_table.schema,
                name=join.right_table.table,
                description=None,
                columns=right_cols_in_join
            )

            qjm = QueryJoinMetadata(
                left_table=left_table_md,
                right_table=right_table_md,
                left_column=left_table_md.columns[0],
                right_column=right_table_md.columns[0],
                join_type=join.join_type,
                join_operator=join.join_operator,
                join_sql=join.join_sql,
                query_metadata=query_metadata,
                yield_relation_nodes=True
            )
            all_joins.append(qjm)
        return all_joins

    def _create_query_metadata(self):
        """
        Creates the following models from the output of a parsed SQL string.
            # 1. Table > Query Relationship
            # 2. Column > Where & Query > Where Relationship
            # 3. Column > Join & Query > Join Relationships
            # 4. Query > Query Execution (aggregation) Relationship
            # 5. TODO: User / table usage (once we have proper user ID mapping)
        """
        results = []
        query_executions = {}

        has_next = True
        while has_next:
            self._create_update_sql_alchemy_extractor()
            batch_cnt = 0

            row = self._alchemy_extractor.extract()
            while row:
                sp = SqlParser(
                    host=self._sql_parser_host,
                    database_type='snowflake',
                    sql=row['query_text'],
                    default_database_name=row['database_name'] or self.snowflake_database,
                    default_schema_name=row['schema_name'] or self.default_schema
                )

                # TODO Look up user somewhere & create TableUsage model
                user = None

                # 1. Table > Query Relationship
                tbl_cols = sp.get_tables_columns()
                query_metadata = self._get_query_metadata(tables_columns=tbl_cols, sql=sp.sql, clean_sql=sp.get_clean_sql(), user=user)
                results.append(query_metadata)

                # Keep track of all "unique" queries. Even though Neo4j will dedupe events for us we can reduce loading
                # time by only emitting unique nodes and relationships. All uniqueness is tracked at the query level.
                if query_metadata.sql_hash not in query_executions:

                    # 2. Column > Where Relationship
                    query_wheres = sp.get_query_wheres()
                    query_wheres = self._get_query_where_metadata(query_wheres=query_wheres, query_metadata=query_metadata)
                    results.extend(query_wheres)

                    # 3. Column > Join & Query > Join
                    tbl_joins = sp.get_tables_joins()
                    query_joins = self._get_query_join_metadata(table_joins=tbl_joins, query_metadata=query_metadata)
                    results.extend(query_joins)

                    query_executions[query_metadata.sql_hash] = {
                        'query_metadata': query_metadata,
                        'exec_count': 0
                    }

                # 4. Query executions
                query_executions[query_metadata.sql_hash]['exec_count'] += 1

                batch_cnt += 1
                row = self._alchemy_extractor.extract()

            if batch_cnt < self.fetch_size:
                has_next = False

        for query in query_executions.values():
            qem = QueryExecutionsMetadata(
                query_metadata=query['query_metadata'],
                execution_count=query['exec_count'],
                start_time=self.start_timestamp_millis,
                window_duration=QueryExecutionsMetadata.EXECUTION_WINDOW_DAILY
            )
            results.append(qem)

        self.iter_results = results

    def _get_extract_iter(self) -> Iterator[QueryMetadata]:
        """
        Using itertools.groupby and raw level iterator, it groups to table and yields QueryMetadata
        :return:
        """
        for r in self.iter_results:
            yield r

    def _create_update_sql_alchemy_extractor(self) -> None:
        """
        Updates the current object's sql alchemy extractor with a new version of the
        `sql_alchemy_extractor.SQLAlchemyExtractor` which has a new sql statement.
        Recreating the sql alchemy extractor is a bit hacky and it is clear it was not designed to
        be able to execute multiple SQL scripts. However, we cannot expect that one SQL to return
        tens or hundrends of thousands of SQL logs will be reasonable.
        """
        # Close any existing connectors
        self._try_close_connector()

        sql_stmt = self.SQL_STATEMENT.format(
            start_timestamp=self.start_timestamp.strftime(self.SNOWFLAKE_TIMESTAMP_FMT),
            end_timestamp=self.end_timestamp.strftime(self.SNOWFLAKE_TIMESTAMP_FMT),
            limit=self.fetch_size,
            offset=self.current_offset
        )
        # Update offset
        self.current_offset += self.fetch_size
        self._alchemy_extractor = sql_alchemy_extractor.from_surrounding_config(self._conf, sql_stmt)
