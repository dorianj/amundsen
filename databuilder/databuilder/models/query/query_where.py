# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import hashlib
import textwrap
from typing import (
    Dict, Iterator, List, Optional
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.query.query import QueryMetadata
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.stemma.sql_parsing.sql_where import WhereAlias


class QueryWhereMetadata(GraphSerializable):
    """
    The Amundsen Query Executions model represents an aggregation for the number
    of times a query was executed within a given time window. Query
    executions are aggregated to time to enable easily adding and
    dropping new query execution aggregations without having to maintain
    all instances that a query was executed in the database.
    # TODO: Is this the right decision below? I'm not sure...
    Furthermore, Query Executions do not contain user information to reduce
    the cardinality and complexity of the data. The User / Table usage
    relationship already exists and provides a high degree of overlap
    for this information.
    """
    NODE_LABEL = 'Where'
    KEY_FORMAT = '{table_hash}-{where_hash}'

    # Relation between table and query
    COLUMN_WHERE_RELATION_TYPE = 'USES_WHERE_CLAUSE'
    INVERSE_COLUMN_WHERE_RELATION_TYPE = 'WHERE_CLAUSE_USED_ON'

    QUERY_WHERE_RELATION_TYPE = 'HAS_WHERE_CLAUSE'
    INVERSE_QUERY_WHERE_RELATION_TYPE = 'WHERE_CLAUSE_OF'

    # Node attributes
    WHERE_CLAUSE = 'where_clause'
    LEFT_ARG = 'left_arg'
    RIGHT_ARG = 'right_arg'
    OPERATOR = 'operator'
    ALIAS_MAPPING = 'alias_mapping'

    def __init__(self,
                 tables: List[TableMetadata],
                 where_clause: str,
                 left_arg: str,
                 right_arg: str,
                 operator: str,
                 query_metadata: QueryMetadata,
                 alias_mapping: Dict[str, WhereAlias],
                 yield_relation_nodes: bool = False):
        self.tables = tables
        self.where_clause = where_clause
        self.left_arg = left_arg
        self.right_arg = right_arg
        self.operator = operator
        self.query_metadata = query_metadata
        self.yield_relation_nodes = yield_relation_nodes
        # Mappings are used by the frontend to allow string substititions
        # and hyperlinks to be built around aliases
        self.alias_mapping = alias_mapping
        self._table_hash = self._get_table_hash(self.tables)
        self._where_hash = self._get_where_hash(self.where_clause)
        self._node_iter = self._create_next_node()
        self._relation_iter = self._create_relation_iterator()

    def __repr__(self) -> str:
        tbl_str = self.tables[0]._get_table_key()
        if len(self.tables) > 1:
            tbl_str += f' + {len(self.tables) - 1} other tables'
        return f'QueryWhereMetadata(Table: {tbl_str}, {self.where_clause[:25]})'

    def _get_table_hash(self, tables: List[TableMetadata]) -> str:
        """
        Generates a unique hash for a set of tables that are associated to a where clause. Since
        we do not want multiple instances of this where clause represented in the database we may
        need to link mulitple tables to this where clause. We do this by creating a single, unique
        key across multiple tables by concatenating all of the table keys together and creating a
        hash (to shorten the value).
        """
        tbl_keys = ''.join(list(sorted([t._get_table_key() for t in tables])))
        return hashlib.md5(tbl_keys.encode('utf-8')).hexdigest()

    def _get_where_hash(self, where_clause: str) -> str:
        """
        Generates a unique hash for a where clause.
        """
        sql_no_fmt = textwrap.dedent(where_clause).replace(' ', '').replace('\n', '').strip().lower()
        return hashlib.md5(sql_no_fmt.encode('utf-8')).hexdigest()

    def create_next_node(self) -> Optional[GraphNode]:
        # return the string representation of the data
        try:
            return next(self._node_iter)
        except StopIteration:
            return None

    def create_next_relation(self) -> Optional[GraphRelationship]:
        try:
            return next(self._relation_iter)
        except StopIteration:
            return None

    @staticmethod
    def get_key(table_hash: str, where_hash: str) -> str:
        return QueryWhereMetadata.KEY_FORMAT.format(table_hash=table_hash, where_hash=where_hash)

    def get_key_self(self) -> str:
        return QueryWhereMetadata.get_key(table_hash=self._table_hash, where_hash=self._where_hash)

    def get_query_relations(self) -> Iterator[GraphRelationship]:
        for table in self.tables:
            for col in table.columns:
                yield GraphRelationship(
                    start_label=ColumnMetadata.COLUMN_NODE_LABEL,
                    end_label=self.NODE_LABEL,
                    start_key=table._get_col_key(col),
                    end_key=self.get_key_self(),
                    type=self.COLUMN_WHERE_RELATION_TYPE,
                    reverse_type=self.INVERSE_COLUMN_WHERE_RELATION_TYPE,
                    attributes={}
                )

        # Optional Query to Where Clause
        if self.query_metadata:
            yield GraphRelationship(
                start_label=QueryMetadata.NODE_LABEL,
                end_label=self.NODE_LABEL,
                start_key=self.query_metadata.get_key_self(),
                end_key=self.get_key_self(),
                type=self.QUERY_WHERE_RELATION_TYPE,
                reverse_type=self.INVERSE_QUERY_WHERE_RELATION_TYPE,
                attributes={}
            )

    def _create_next_node(self) -> Iterator[GraphNode]:
        """
        Create query nodes
        :return:
        """
        yield GraphNode(
            key=self.get_key_self(),
            label=self.NODE_LABEL,
            attributes={
                self.WHERE_CLAUSE: self.where_clause,
                self.LEFT_ARG: self.left_arg,
                self.RIGHT_ARG: self.right_arg,
                self.OPERATOR: self.operator,
                self.ALIAS_MAPPING: {
                    alias_item.alias: {
                        'database': self.tables[0].database,  # All tables should share the same database
                        'cluster': alias_item.table.cluster,
                        'schema': alias_item.table.schema,
                        'name': alias_item.table.table
                    }
                    for alias_item in self.alias_mapping.values()
                }
            }
        )
        if self.yield_relation_nodes:
            for table in self.tables:
                for tbl_item in table._create_next_node():
                    yield tbl_item
            if self.query_metadata:
                for query_item in self.query_metadata._create_next_node():
                    yield query_item

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        relations = self.get_query_relations()
        for relation in relations:
            yield relation

        if self.yield_relation_nodes:
            for table in self.tables:
                for tbl_rel in table._create_next_relation():
                    yield tbl_rel
            if self.query_metadata:
                for query_rel in self.query_metadata._create_relation_iterator():
                    yield query_rel
