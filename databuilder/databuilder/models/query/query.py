# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import hashlib
import re
import textwrap
from typing import (
    Iterator, List, Optional, Union,
)

from databuilder.models.graph_node import GraphNode
from databuilder.models.graph_relationship import GraphRelationship
from databuilder.models.graph_serializable import GraphSerializable
from databuilder.models.table_serializable import TableSerializable
from databuilder.models.table_metadata import TableMetadata
from databuilder.models.user import User as UserMetadata


class QueryMetadata(GraphSerializable):
    """
    Query model. This creates a Query object as well as relationships
    between the Query and the Table(s) that are used within the query.
    The full key for the tables must be provided as part of the constructor.
    Optionally, the ID of the user that executed the query can be
    provided as well. The user must already exist in the database for
    the Query to User connection to be created.
    """
    NODE_LABEL = 'Query'
    KEY_FORMAT = '{sql_hash}'

    # Relation between entity and query
    TABLE_QUERY_RELATION_TYPE = 'HAS_QUERY'
    INVERSE_TABLE_QUERY_RELATION_TYPE = 'QUERY_FOR'

    USER_QUERY_RELATION_TYPE = 'EXECUTED_QUERY'
    INVERSE_USER_QUERY_RELATION_TYPE = 'EXECUTED_BY'

    # Attributes
    SQL = 'sql'
    TABLES = 'tables'

    def __init__(
        self,
        sql: str,                           # Full SQL for a given Query
        tables: List[TableMetadata],        # List of table keys corresponding to tables in the query
        clean_sql: str = None,               # A modified sql that should be used to create the hash if available
        user: UserMetadata = None,          # Key for the user that executed the query
        yield_relation_nodes: bool = False  # Allow creation of related nodes if they do not exist
    ):
        self.sql = sql
        self.clean_sql = clean_sql
        self.sql_hash = self._get_sql_hash(clean_sql or sql)
        self.tables = tables
        self.table_keys = [tm._get_table_key() for tm in tables]
        self.user = user
        self.yield_relation_nodes = yield_relation_nodes
        self._sql_begin = sql[:25] + '...'
        self._node_iter = self._create_next_node()
        self._relation_iter = self._create_relation_iterator()

    def __repr__(self) -> str:
        return f'QueryMetadata(SQL: {self._sql_begin}, Tables: {self.table_keys})'

    def _get_sql_hash(self, sql) -> str:
        """
        Generates a unique SQL hash. Attempts to remove any formatting from the
        SQL code where possible.
        """
        sql_no_fmt = (
            textwrap.dedent(sql)
            .replace('\n', '')
            .replace(';', '')
            .replace(' ', '')
            .replace('"', '')
            .replace("'", '')
            .strip()
            .lower()
        )
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
    def get_key(sql_hash) -> str:
        return QueryMetadata.KEY_FORMAT.format(sql_hash=sql_hash)

    def get_key_self(self) -> str:
        return QueryMetadata.get_key(self.sql_hash)

    def get_query_relations(self) -> List[GraphRelationship]:
        relations = []
        for table_key in self.table_keys:
            table_relation = GraphRelationship(
                start_label=TableMetadata.TABLE_NODE_LABEL,
                end_label=self.NODE_LABEL,
                start_key=table_key,
                end_key=self.get_key_self(),
                type=self.TABLE_QUERY_RELATION_TYPE,
                reverse_type=self.INVERSE_TABLE_QUERY_RELATION_TYPE,
                attributes={}
            )
            relations.append(table_relation)

        if self.user:
            user_relation = GraphRelationship(
                start_label=UserMetadata.USER_NODE_LABEL,
                end_label=self.NODE_LABEL,
                start_key=self.user.get_user_model_key(email=self.user.email),
                end_key=self.get_key_self(),
                type=self.USER_QUERY_RELATION_TYPE,
                reverse_type=self.INVERSE_USER_QUERY_RELATION_TYPE,
                attributes={}
            )
            relations.append(user_relation)
        return relations

    def _create_next_node(self) -> Iterator[GraphNode]:
        """
        Create query nodes
        :return:
        """
        yield GraphNode(
            key=self.get_key_self(),
            label=self.NODE_LABEL,
            attributes={
                self.SQL: self.sql
            }
        )
        if self.yield_relation_nodes:
            for table in self.tables:
                for tbl_item in table._create_next_node():
                    yield tbl_item
            if self.user:
                for usr_item in self.user._create_next_node():
                    yield usr_item

    def _create_relation_iterator(self) -> Iterator[GraphRelationship]:
        relations = self.get_query_relations()
        for relation in relations:
            yield relation

        if self.yield_relation_nodes:
            for table in self.tables:
                for tbl_rel in table._create_next_relation():
                    yield tbl_rel
            if self.user:
                for usr_rel in self.user._create_relation_iterator():
                    yield usr_rel