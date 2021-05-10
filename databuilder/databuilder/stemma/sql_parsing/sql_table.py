
from typing import List


class SqlTable(object):
    """
    Simple object holder for a table. Receives a table reference, which may look like
    any of the following:
        - cluster.schema.table
        - schema.table
        - table
    These values are parsed out and, where applicable, uses default values to fill
    in the missing cluster and schema. The output of this is generally used to
    build a TableMetadata object
    """
    def __init__(self, table_reference: str, default_cluster: str, default_schema: str) -> None:
        self.table_reference = table_reference
        self.default_cluster = default_cluster
        self.default_schema = default_schema
        self.columns: List[str] = []

        # TableMetadata attributes
        self.cluster: str = default_cluster
        self.schema: str = default_schema
        self.table: str = table_reference
        self._set_values()

    def _set_values(self) -> None:
        """
        Parses out the original table reference and fill in the cluster,
        schema and table where required.
        """
        tbl_ref_split = self.table_reference.split('.')
        if len(tbl_ref_split) == 1:
            self.cluster = self.default_cluster
            self.schema = self.default_schema
            self.table = tbl_ref_split[0]
        elif len(tbl_ref_split) == 2:
            self.cluster = self.default_cluster
            self.schema = tbl_ref_split[0]
            self.table = tbl_ref_split[1]
        else:
            # There "shouldn't" be more than 3 items here
            self.cluster = tbl_ref_split[0]
            self.schema = tbl_ref_split[1]
            self.table = tbl_ref_split[2]

    @property
    def table_id(self) -> str:
        return f'{self.cluster}.{self.schema}.{self.table}'
